# -*- coding:utf-8 -*-
# __author__ = majing
"""
具体采集，校验函数
"""
import json
import logging
import datetime

from odps.errors import ETParseError
from superset.monitor.base import get_odps
from superset.monitor.validates.models import ValidateErrorRule
from superset.models.core_ext import MProject, MPage
from superset.monitor.utils import to_html, send_mail, report_template
from superset.monitor.validates.models import ValidateRecord
from superset.monitor.tasks.models import TaskRecord
from superset.monitor.alarms.models import AlarmRecord

from .sync_king import SupersetMemcached

odps_app = get_odps()


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
            cls.alarm_send_mail(alarm.user, content)
        except Exception as exc:
            return False, str(exc)
        return True, ''

    @classmethod
    def alarm_send_mail(cls, users, html):
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


class ValidateInter(object):

    @classmethod
    def __get_md_pds(cls, session):
        querys = session.query(MProject).all()
        values = [query.id for query in querys]
        logging.info("project id:  count:%s       values:%s" % (len(values), values))
        return tuple(values)

    @classmethod
    def __get_md_pads(cls, session):
        querys = session.query(MPage).all()
        values = [query.page_id for query in querys]
        logging.info("project page id: count:%s   values:%s" % (len(values), values))
        return tuple(values)

    @classmethod
    def __get_pro_table_name(cls, pro_name, tb_name):
        return "%s.%s" % (pro_name, tb_name)

    @classmethod
    def __get_validate_error(cls, pro_name, tab_name, session):
        """
        获取一个表的错误校验配置
        """
        return ValidateErrorRule.get_table_error_conf(pro_name, tab_name, session)

    @classmethod
    def get_func_result(cls, sql):
        """
        获取校验函数中的sql的执行结果，调用此函数的校验函数属于func类型
        """
        is_error = False
        logging.info("execute sql: %s" % sql)
        try:
            instance = odps_app.execute_sql(sql)

            with instance.open_reader() as reader:
                for record in reader:
                    values = record.values
                    logging.info("record values: %s" % values)
                    if values[0] > 1:
                        is_error = True
                    break
        except (ETParseError, Exception) as exc:
            raise ValueError("get_func_result error: %s" % str(exc))

        return is_error

    @classmethod
    def get_sql_result(cls, sql):
        """
        获取校验函数的sql的执行结果，调用此函数的校验函数属于sql类型
        """
        value = None
        try:
            instance = odps_app.execute_sql(sql)

            with instance.open_reader() as reader:
                for record in reader:
                    values = record.values
                    logging.info("record values: %s" % values)
                    if values[0]:
                        value = values[0]
        except (ETParseError, Exception) as exc:
            raise ValueError(u"执行sql失败: %s" % str(exc))

        return value

    @classmethod
    def get_table_partition_count(cls, sql, name, partition):
        count = 0
        instance = odps_app.execute_sql(sql)

        with instance.open_reader() as reader:
            for record in reader:
                values = record.values
                logging.info("[%s] in [%s]  total count: %s" % (name, partition, values))
                count = values[0]
        return count

    @classmethod
    def repeat(cls, validate, **kwargs):
        """
        重复数据校验
        """
        is_has_error = False
        error_pt = []
        partitions = validate.partition
        fields = validate.repeat_fields

        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)
        for pt in partitions:
            for item in fields:
                sql = "select count(*) as num from %s where %s GROUP BY %s HAVING num > 1 limit 1;" % (pro_tab_name, pt,
                                                                                                 ','.join(item))
                is_error = cls.get_func_result(sql)
                if is_error:
                    error_pt.append(pt)

        if not error_pt:
            error_msg = u"表[%s]的[%s]没有重复值.分区: %s" % (pro_tab_name, fields, partitions)
        else:
            is_has_error = True
            error_msg = u"表[%s]的[%s]在分区%s有重复值." % (pro_tab_name, fields, partitions)

        return is_has_error, error_msg

    @classmethod
    def missing(cls, validate, **kwargs):
        """
        缺失数据
        """
        is_has_error = False
        error_pt = []
        partitions = validate.partition
        fields = validate.missing_fields
        filters = ""
        for name in fields:
            filters += "(%s is NULL) or " % name
        filters = filters.lstrip()
        filters = filters[: -3]
        logging.info("missing: filter: %s" % filters)

        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)

        for pt in partitions:
            sql = "select count(*) from %s where %s and (%s) ;" % (pro_tab_name, pt, filters)
            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)

        if not error_pt:
            error_msg = u"表[%s]的[%s]没有缺失值.分区: %s" % (pro_tab_name, fields, partitions)
        else:
            is_has_error = True
            error_msg = u"表[%s]的[%s]在分区%s有缺失值." % (pro_tab_name, fields, partitions)

        return is_has_error, error_msg

    @classmethod
    def tb_count(cls, rule):
        """
        表数据量
        """
        print('table column count ...')

    @classmethod
    def db_count(cls, rule):
        """
        数据库中表的数量
        """
        print('database table count ....')

    @classmethod
    def error(cls, validate, session=None):
        """
        错误校验 
        """
        key = "%s.%s" % (validate.pro_name, validate.tab_name)
        is_has_error = False
        error_msg = "表[%s]  " % key

        error_conf = cls.__get_validate_error(validate.pro_name, validate.tab_name, session)
        if error_conf:
            try:
                conf = json.loads(error_conf.rule)
            except Exception as e:
                error_msg = "[%s] error validate error: error rule: %s     msg: %s" % (key, error_conf.rule, str(e))
            else:
                logging.info("error conf: %s" % conf)
                for field, func in conf.items():
                    result = getattr(cls, func)(validate, field, session=session)
                    if result:
                        is_has_error = True
                        error_msg += "字段[%s]在分区%s中有错误值\n" % (field, result)
                    else:
                        error_msg += "字段[%s]没有错误值\n" % field

        else:
            error_msg = u"表[%s]没有配置错误校验规则." % key
        return is_has_error, error_msg

    @classmethod
    def validate_user_id(cls, validate, field, length=10, **kwargs):
        """
        校验用户ID
        :return: 
        """
        error_pt = []
        partitions = validate.partition
        logging.info("validate_user_id: partitions: %s" % partitions)
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name,validate.tab_name)

        for pt in partitions:
            sql = "select count(*) from %s where %s and (LENGTH(%s) > %s or %s rlike '([^0-9]+[0-9]+[^0-9]*)|([0-9]+[^0-9]+[^0-9]*)|([^0-9]*+[0-9]+[^0-9]+)') ;" % (
                pro_tab_name, pt, field, length, field)
            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)
        return error_pt

    @classmethod
    def validate_pro_id(cls, validate, field, session=None):
        """
        校验项目ID
        :return: 
        """
        error_pt = []

        pds = cls.__get_md_pds(session)
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)

        partitions = validate.partition
        logging.info("validate_pro_id: partitions: %s" % partitions)

        for pt in partitions:
            sql = "select count(*) from %s where %s and pd not in %s ;" % (pro_tab_name, pt, pds)
            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)
        return error_pt

    @classmethod
    def validate_page_id(cls, validate, field, session=None):
        """
        校验页面ID
        :return: 
        """
        error_pt = []

        pads = cls.__get_md_pads(session)
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)
        partitions = validate.partition
        logging.info("validate_page_id: partitions: %s" % partitions)

        for pt in partitions:
            sql = "select count(*) from %s where %s and pad not in %s ;" % (pro_tab_name, pt, pads)
            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)
        return error_pt

    @classmethod
    def validate_time(cls, validate, field, **kwargs):
        """
        校验时间戳
        :return: 
        """
        error_pt = []

        partitions = validate.partition
        logging.info("validate_time: partitions: %s" % partitions)

        min_time = '1970-01-01 00:00:00'
        max_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name,validate.tab_name)

        for pt in partitions:
            sql = "select count(*) from %s where %s and (from_unixtime(%s/1000)<'%s' or from_unixtime(%s/1000)>'%s' );" % \
                  (pro_tab_name, pt, field, min_time, field, max_time)

            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)
        return error_pt

    @classmethod
    def logic_validate(cls, validate, **kwargs):
        """
        逻辑校验
        :return: 
        """
        is_has_error = False
        error_msg = ''

        old_total_count, new_total_count = (0, 0)
        if validate.is_multi_days:
            end_time = validate.end_time
            start_time = validate.start_time
        else:
            end_time = datetime.datetime.now() - datetime.timedelta(days=1)
            start_time = datetime.datetime.now() - datetime.timedelta(days=1)
        do_start_time = start_time
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)
        table = odps_app.get_table(validate.tab_name, project=validate.pro_name)
        if 'dm' in table.name and table.schema.partitions:
            while do_start_time <= end_time:
                pt_end_time = (do_start_time - datetime.timedelta(days=2)).strftime("%Y%m%d")
                pt_start_time = (do_start_time - datetime.timedelta(days=8)).strftime("%Y%m%d")
                partition = "day>=%s and day<=%s" % (pt_start_time, pt_end_time)
                sql = "select count(*) from %s WHERE %s;" % (pro_tab_name, partition)
                old_total_count += cls.get_table_partition_count(sql, pro_tab_name, partition)

                new_date = (do_start_time - datetime.timedelta(days=1)).strftime("%Y%m%d")
                partition = "day=%s" % new_date
                sql = "select count(*) from %s WHERE %s;" % (pro_tab_name, partition)
                new_total_count += cls.get_table_partition_count(sql, pro_tab_name, partition)

                avg = old_total_count/7.0
                if int(avg * 0.5) <= new_total_count <= int(avg * 1.5):
                    do_start_time = do_start_time + datetime.timedelta(days=1)
                    continue

                is_has_error = True
                msg = "[分区]:%s   [表名]:%s  [7天平均值]:%s [当天数据量]:%s" % (pro_tab_name, partition, avg,
                                                                    new_total_count)
                error_msg += "%s\n" % msg
                do_start_time = do_start_time + datetime.timedelta(days=1)
        else:
            is_has_error = True
            error_msg = "只有集市表进行逻辑校验.表[%s]不是集市表或者表没有分区" % pro_tab_name

        if not is_has_error:
            error_msg = u"表[%s]在[%s ~ %s]没有错误值." % (pro_tab_name, start_time.strftime("%Y%m%d"),
                                                    end_time.strftime("%Y%m%d"))

        return is_has_error, error_msg

    @classmethod
    def sync_king_minute(cls, validate, session=None, **kwargs):
        is_error = False
        msg = '金刚缓存每5分钟同步成功'
        try:
            superset = SupersetMemcached(table_conf=json.loads(validate.fields), session=session)
            error_add_tabs, error_add_columns = superset.set_minute()
            if error_add_tabs or error_add_columns:
                is_error = True
                msg = "添加失败的表: %s\n   添加失败的列: %s" % (error_add_tabs, error_add_columns)

        except Exception as exc:
            is_error = True
            msg = u"金刚缓存同步失败：%s" % str(exc)

        return is_error, msg

    @classmethod
    def sync_king_day(cls, validate, session=None, **kwargs):
        try:
            superset = SupersetMemcached(table_conf=json.loads(validate.fields), session=session)
            error_update_info = superset.set_day()
            if error_update_info:
                is_error = True
                msg = u"执行失败：更新失败的表和字段信息： %s" % error_update_info
            else:
                is_error = False
                msg = u"金刚缓存每天同步成功"
        except Exception as exc:
            is_error = True
            msg = u"金刚缓存每天同步失败：%s" % str(exc)
        return is_error, msg

    @classmethod
    def execute_sql(cls, validate, **kwargs):
        is_error = False
        msg = '[%s]没有有错误值' % validate.name
        if validate.sql_expression:
            value = cls.get_sql_result(validate.sql_expression)
            if value > validate.compare_v:
                is_error = True
                msg = '[%s]有错误值' % validate.name
        return is_error, msg
            


