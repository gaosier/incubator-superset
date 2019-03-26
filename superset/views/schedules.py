# -*- coding:utf-8 -*-
# __author__ = majing

"""
定时任务优化(2019/3/21):
1. 删除不用的字段，添加新字段
2. 新增复制功能
"""

# pylint: disable=C,R,W
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import uuid
import json
from flask import request
from croniter import croniter
from flask_appbuilder import expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import has_access

from flask_babel import gettext as __
from flask_babel import lazy_gettext as _

from apscheduler.triggers.cron import CronTrigger

from superset import appbuilder, flask_scheduler, aps_logger
from superset.exceptions import SupersetException
from superset.models.core import Dashboard, Slice
from superset.models.schedules import DashboardEmailSchedule, ScheduleType, SliceEmailSchedule, db

from superset.utils import get_email_address_list
from .base import SupersetModelView, api, json_success
from .base_ext import login_required

EMAIL_TYPE = {"dash": DashboardEmailSchedule, "slice": SliceEmailSchedule}

class EmailScheduleView(SupersetModelView):
    description_columns = {
        'deliver_as_group': '如果选择了，邮件的接收人是所有的成员',
        'crontab': 'Unix crontab 表达式',
        'delivery_type': 'Inline:在正文里   Attachment:附件',
    }

    def pre_add(self, obj):
        try:
            recipients = get_email_address_list(obj.recipients)
            obj.recipients = ', '.join(recipients)
        except Exception:
            raise SupersetException(u'邮件列表格式不正确')

        if not croniter.is_valid(obj.crontab):
            raise SupersetException(u'crontab格式不正确')

        obj.job_id = str(uuid.uuid4())

        if obj.active:
            self.add_apscheduler_job(obj)

    def pre_delete(self, item):
        """
        删除定时任务时，删除apscheduler中的job
        """
        job_id = item.job_id
        job = flask_scheduler.get_job(job_id)
        if job:
            flask_scheduler.remove_job(job_id)

    def add_apscheduler_job(self, task):
        from superset.tasks.schedules import schedule_email_report
        recipients = task.recipients
        args = (self.schedule_type, task.id)
        kwargs = dict(recipients=recipients)

        try:
            flask_scheduler.add_job(task.job_id, schedule_email_report, args=args, kwargs=kwargs,
                                    replace_existing=True,
                                    trigger=CronTrigger.from_crontab(task.crontab), name=task.name)
            aps_logger.info("添加定时任务成功: name:%s  job_id:%s " % (task.name, task.job_id))
        except Exception as exc:
            msg = "添加定时任务失败：name:%s  job_id: %s  msg:%s" % (task.name, task.job_id, exc)
            aps_logger.error(msg)
            raise SupersetException(msg)

    def pre_update(self, obj):
        try:
            recipients = get_email_address_list(obj.recipients)
            obj.recipients = ', '.join(recipients)
        except Exception:
            raise SupersetException(u'邮件列表格式不正确')

        if not croniter.is_valid(obj.crontab):
            raise SupersetException(u'crontab格式不正确')


    def get_model_cls(self, param):
        keys = EMAIL_TYPE.keys()
        if param not in keys:
            raise SupersetException(u"参数[type]取值错误! 取值范围:%s" % keys)
        return EMAIL_TYPE.get(param)

    @api
    @expose('/copy/', methods=('POST',))
    @login_required
    def copy_dash(self):
        """
        复制定时任务
        """
        task_ids = request.form.getlist('task_ids', [])
        _type = request.form.get('type', 'dash')

        model_cls = self.get_model_cls(_type)
        instances = model_cls.get_instances(task_ids)

        for item in instances:
            task = model_cls()
            task.name = item.name + '[copy]'
            task.delivery_type = item.delivery_type
            task.recipients = item.recipients
            task.crontab = item.crontab
            task.mail_content = item.mail_content
            task.deliver_as_group = item.deliver_as_group
            task.comment = item.comment
            task.slice_data = item.slice_data
            task.job_id = str(uuid.uuid4())

            if _type == 'dash':
                task.dashboard_id = item.dashboard_id
            else:
                task.slice_id = item.slice_id
                task.email_format = item.email_format

            try:
                self.add_apscheduler_job(task)
            except (SupersetException, Exception) as exc:
                raise SupersetException(u"复制定时任务失败。错误原因：%s " % str(exc))
            else:
                db.session.add(item)
                db.session.commit()

        return json_success(u"复制定时任务成功!!!")

    @api
    @expose('/enable/', methods=('POST',))
    @login_required
    def enable(self):
        """
        对定时任务进行启用禁用操作
        """
        task_ids = request.form.getlist('task_ids', [])
        _type = request.form.get('type', 'dash')

        model_cls = self.get_model_cls(_type)
        instances = model_cls.get_instances(task_ids)

        for item in instances:
            job_id = item.job_id
            status = item.active

            job = flask_scheduler.get_job(job_id, 'default')
            if not job:
                raise SupersetException(u"找不到看板邮件任务的定时任务！任务名字:%s " % item.name)

            try:
                if status:
                    job.pause()
                else:
                    job.resume()
            except Exception as exc:
                msg = "apscheduler[禁用/启用]任务失败：job_id:%s  name:%s  msg:%s " % (job_id, item.name, str(exc))
                aps_logger.error(msg)
                raise SupersetException(msg)
            else:
                item.active = not status
                db.session.add(item)
                db.session.commit()
        return json_success(u"设置定时任务状态成功!!!")

    @api
    @expose('/check/jobs/', methods=('POST',))
    @login_required
    def check_jobs(self):
        """
        校验数据一致性  apscheduler中的job是否存在
        """
        errors = []

        task_ids = request.form.getlist('task_ids', [])
        _type = request.form.get('type', 'dash')

        model_cls = self.get_model_cls(_type)
        instances = model_cls.get_instances(task_ids)

        for item in instances:
            job_id = item.job_id
            job = flask_scheduler.get_job(job_id, 'default')
            if not job:
                errors.append(item.name)

        msg = u"定时任务的apscheduler job都存在" if not errors else u"apscheduler任务不存在的看板邮件任务：%s" % ', '.join(errors)
        return json_success(msg)

    @api
    @expose('/multi/delete/', methods=('POST',))
    @login_required
    def multi_delete(self):
        """
        批量删除 
        """
        task_ids = request.form.getlist('task_ids', [])
        _type = request.form.get('type', 'dash')

        model_cls = self.get_model_cls(_type)
        instances = model_cls.get_instances(task_ids)

        for task in instances:
            job_id = task.job_id
            try:
                flask_scheduler.remove_job(job_id, 'default')
            except Exception as exc:
                raise SupersetException(u"apscheduler删除job失败: %s " % str(exc))
            else:
                task.delete_instance()
        return json_success(u"删除定时任务成功!!!")

    @api
    @expose('/modify/name/', methods=['POST'])
    @login_required
    def modify_name(self):
        """
        修改名字
        :return: 
        """
        pk = request.form.get('pk')
        new_name = request.form.get('name')
        _type = request.form.get('type')

        model_cls = self.get_model_cls(_type)
        instance = model_cls.get_instance_by_id(pk)
        if not instance:
            raise SupersetException(u"找不到定时任务。pk:%s  type: %s " % (pk, _type))

        job_id = instance.job_id

        try:
            flask_scheduler.modify_job(job_id, jobstore='default', name=new_name)
        except Exception as exc:
            raise SupersetException(u"修改定时任务名字失败: %s" % str(exc))

        instance.name = new_name
        db.session.add(instance)
        db.session.commit()

    @api
    @expose('/modify/corntab/')
    @login_required
    def modify_corntab(self):
        """
        修改定时时间
        :return: 
        """
        pk = request.form.get('pk')
        crontab = request.form.get('crontab')
        _type = request.form.get('type')

        model_cls = self.get_model_cls(_type)
        instance = model_cls.get_instance_by_id(pk)
        if not instance:
            raise SupersetException(u"找不到定时任务。pk:%s  type: %s " % (pk, _type))

        job_id = instance.job_id

        try:
            flask_scheduler.reschedule_job(job_id, jobstore='default', trigger=CronTrigger.from_crontab(crontab))
        except Exception as exc:
            raise SupersetException(u"修改定时任务的运行时间失败: %s" % str(exc))

        instance.crontab = crontab
        db.session.add(instance)
        db.session.commit()

    @api
    @expose('/list/', methods=['POST'])
    @login_required
    def list(self):
        """
        列表
        :return: 
        """
        _type = request.form.get('type')
        model_cls = self.get_model_cls(_type)

        data = model_cls.get_list()
        return json_success(json.dumps(data))


class DashboardEmailView(EmailScheduleView):
    schedule_type = ScheduleType.dashboard.name
    schedule_type_model = Dashboard
    add_title = '添加看板定时邮件'
    edit_title = '编辑看板定时邮件'
    list_title = "看板定时邮件"
    show_title = "看板定时任务详情"
    datamodel = SQLAInterface(DashboardEmailSchedule)
    order_columns = ['created_on']
    list_columns = ['name', 'dashboard', 'is_active', 'crontab', 'creator', 'is_deliver_as_group', 'delivery_type',
                    'is_slice_data']

    add_columns = ['name', 'dashboard', 'active', 'crontab', 'recipients', 'deliver_as_group', 'delivery_type',
                   'slice_data', 'mail_content', 'comment']

    edit_columns = ['dashboard',  'crontab', 'recipients', 'deliver_as_group', 'delivery_type', 'slice_data',
                    'mail_content', 'comment']

    show_columns = ['name', 'dashboard', 'is_active', 'crontab', 'recipients', 'is_deliver_as_group', 'delivery_type',
                   'is_slice_data', 'mail_content', 'creator', 'job_id', 'comment']

    search_columns = ['dashboard','active', 'deliver_as_group', 'delivery_type']
    label_columns = {
        'name': _('Name'),
        'dashboard': _('Dashboard'),
        'created_on': _('Created On'),
        'changed_on': _('Changed On'),
        'is_active': _('Active'),
        'crontab': _('Crontab'),
        'recipients': _('Recipients'),
        'is_deliver_as_group': _('Deliver As Group'),
        'deliver_as_group': _('Deliver As Group'),
        'delivery_type': _('Delivery Type'),
        'is_slice_data':_('Slice data'),
        'slice_data': _('Slice data'),
        'mail_content':_('Mail content'),
        'comment': _('Comment'),
        'creator': _('Creator'),
        'job_id': _('Job Id')
    }


class SliceEmailView(EmailScheduleView):
    schedule_type = ScheduleType.slice.name
    schedule_type_model = Slice
    add_title = '添加报表定时邮件'
    edit_title = '编辑报表定时邮件'
    list_title = '报表定时邮件'
    datamodel = SQLAInterface(SliceEmailSchedule)
    order_columns = ['slice', 'created_on']
    list_columns = ['name','slice', 'active', 'crontab', 'deliver_as_group', 'delivery_type', 'email_format']

    add_columns = ['name', 'slice', 'active', 'crontab', 'recipients', 'deliver_as_group', 'delivery_type',
                   'email_format', 'comment']
    edit_columns = add_columns

    search_columns = ['slice', 'active', 'deliver_as_group', 'delivery_type', 'email_format']
    label_columns = {
        'slice': _('Chart'),
        'created_on': _('Created On'),
        'changed_on': _('Changed On'),
        'active': _('Active'),
        'crontab': _('Crontab'),
        'recipients': _('Recipients'),
        'deliver_as_group': _('Deliver As Group'),
        'delivery_type': _('Delivery Type'),
        'email_format': _('Email Format'),
        'comment': _('Comment'),
        'creator': _('Creator')
    }


appbuilder.add_separator('Manage')
appbuilder.add_view(
    DashboardEmailView,
    'Dashboard Emails',
    label=__('Dashboard Emails'),
    category='Manage',
    category_label=__('Manage'),
    icon='fa-search')

appbuilder.add_view(
    SliceEmailView,
    'Chart Email',
    label=__('Chart Email'),
    category='Manage',
    category_label=__('Manage'),
    icon='fa-search')
