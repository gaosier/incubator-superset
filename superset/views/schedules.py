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


class EmailScheduleView(SupersetModelView):
    schedule_type = None
    schedule_type_model = None
    page_size = 20
    add_exclude_columns = ['created_on','changed_on','created_by', 'changed_by']
    edit_exclude_columns = add_exclude_columns
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


    @api
    @expose('/copy/', methods=('POST',))
    def copy_dash(self):
        """
        复制定时任务
        """
        dash_ids = request.form.getlist('dash_ids', [])
        dash_tasks = DashboardEmailSchedule.get_instances(dash_ids)
        for item in dash_tasks:
            task = DashboardEmailSchedule()
            task.name = item.name + '[copy]'
            task.delivery_type = item.delivery_type
            task.recipients = item.recipients
            task.crontab = item.crontab
            task.mail_content = item.mail_content
            task.dashboard_id = item.dashboard_id
            task.deliver_as_group = item.deliver_as_group
            task.comment = item.comment
            task.slice_data = item.slice_data
            task.job_id = str(uuid.uuid4())

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
    def enable(self):
        """
        对定时任务进行启用禁用操作
        """
        dash_ids = request.form.getlist('dash_ids', [])
        dash_tasks = DashboardEmailSchedule.get_instances(dash_ids)
        for item in dash_tasks:
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
    def check_jobs(self):
        """
        校验数据一致性  看板的任务的定时邮件是否都存在
        """
        errors = []
        dash_ids = request.form.getlist('dash_ids', [])
        dash_tasks = DashboardEmailSchedule.get_instances(dash_ids)
        for item in dash_tasks:
            job_id = item.job_id
            job = flask_scheduler.get_job(job_id, 'default')
            if not job:
                errors.append(item.name)

        if not errors:
            msg = u"看板任务对应的apscheduler任务都存在"
        else:
            msg = u"apscheduler任务不存在的看板邮件任务：%s" % ', '.join(errors)

        return json_success(msg)

    @api
    @expose('/multi/delete/', methods=('POST',))
    def multi_delete(self):
        """
        批量删除 
        """
        dash_ids = request.form.getlist('dash_ids', [])
        dash_tasks = DashboardEmailSchedule.get_instances(dash_ids)
        for task in dash_tasks:
            job_id = task.job_id
            try:
                flask_scheduler.remove_job(job_id, 'default')
            except Exception as exc:
                raise SupersetException(u"apscheduler删除job失败: %s " % str(exc))
            else:
                task.delete_instance()
        return json_success(u"删除定时任务成功!!!")

    # @api
    # @has_access
    # @expose('/list/', methods=['POST'])
    # def list(self):
    #     data = DashboardEmailSchedule.get_list()
    #     return json_success(json.dumps(data))

    @api
    @expose('/modify/name/<dash_id>/', methods=['POST'])
    def modify_name(self):
        """
        修改名字
        :return: 
        """
        pass

    @api
    @expose('/modify/corntab/<dash_id>/')
    def modify_corntab(self):
        """
        修改定时时间
        :return: 
        """
        pass


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
