# -*- coding:utf-8 -*-
# __author__ = majing

"""
发邮件，生成记录接口
"""
from superset.monitor.utils import to_html, send_mail, report_template
from superset.monitor.validates.models import ValidateRecord
from superset.monitor.tasks.models import TaskRecord
from superset.monitor.alarms.models import AlarmRecord


class GenRecord(object):

    _record_cls = { "ValidateRecord": ValidateRecord, "AlarmRecord": AlarmRecord}

    @classmethod
    def create_record(cls, cls_name, **kwargs):
        if cls_name in cls._record_cls:
            record_id = cls._record_cls.get(cls_name).add_task_record(**kwargs)
        else:
            record_id = None
        return record_id


class AlarmInter(object):

    @classmethod
    def alarm(cls, alarm, task_name, task_record_id, validate_record_ids, session):
        try:
            content = cls.gen_mail_html(task_name, task_record_id, validate_record_ids, session)
            if content:
                cls.alarm_send_mail(alarm.user, content)
        except Exception as exc:
            return False, str(exc)
        return True, ''

    @classmethod
    def alarm_table_html(cls, alarm, htmls):
        try:
            if htmls:
                cls.alarm_send_mail(alarm.user, htmls)
        except Exception as exc:
            return False, str(exc)
        return True, ''

    @classmethod
    def alarm_send_mail(cls, users, html):
        user_id_email_map = {user.id: user.email for user in users}
        if isinstance(html, list):
            for content in html:
                if 'all' in content:
                    to_mails = [user.email for user in users]
                    if content.get('all'):
                        send_mail(content.get('all'), to_mails)
                else:
                    for user_id, value in content.items():
                        if value:
                            to_mails = [user_id_email_map.get(user_id)]
                            send_mail(value, to_mails)
        else:
            to_mails = [user.email for user in users]
            send_mail(html, to_mails)

    @classmethod
    def gen_mail_html(cls, task_name, task_record_id, validate_record_ids, session):
        task_record_html = cls.gen_task_record_html(task_record_id, session)
        validate_record_html = cls.gen_validate_record_html(validate_record_ids, session)
        html = report_template(task_name, task_record_html, validate_record_html)
        return html

    @classmethod
    def gen_task_record_html(cls, record_id, session):
        columns = ['task_name', 'is_success', 'duration', 'reason']
        record = TaskRecord.get_task_record_by_id(record_id, session)
        record_list = []
        for col in columns:
            if col == 'duration':
                value = getattr(record, 'changed_on') - getattr(record, 'created_on')
            else:
                value = getattr(record, col)
            record_list.append(value)
        record_html = to_html([u'任务名称', u'执行结果', u'执行时长', u'详情'], [record_list])
        return record_html

    @classmethod
    def gen_validate_record_html(cls, record_ids, session):
        columns = ['task_name',  'validate_rule_name', 'operation', 'is_success', 'reason']
        values = []
        for record_id in record_ids:
            record_list = []
            record = ValidateRecord.get_records_by_id(record_id, session)
            for col in columns:
                record_list.append(getattr(record, col))
            values.append(record_list)
        record_html = to_html([u'任务名称', u"校验规则", u"校验类型", u'执行结果', u'详情'], values)
        return record_html



            


