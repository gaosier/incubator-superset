# -*- coding:utf-8 -*-
# __author__ = majing
# pylint: disable=no-member

"""定时发送邮件模块"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import enum
from flask import g
from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders
from sqlalchemy import (
    Boolean, Column, Enum, ForeignKey, Integer, Text, String
)
from sqlalchemy.orm import relationship

from superset import db
from superset.models.helpers import AuditMixinNullable
from superset.custom_user.sec_models import MyUser

metadata = Model.metadata


class ScheduleType(enum.Enum):
    slice = 'slice'
    dashboard = 'dashboard'


class EmailDeliveryType(enum.Enum):
    attachment = 'Attachment'
    inline = 'Inline'


class SliceEmailReportFormat(enum.Enum):
    visualization = 'Visualization'
    data = 'Raw data'


class EmailSchedule(object):
    """
      发送邮件
    """
    __tablename__ = 'email_schedule'
    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    active = Column(Boolean, default=True)
    slice_data = Column(Boolean, default=True, comment=u"是否发送报表内容")
    crontab = Column(String(50))
    comment = Column(String(150))
    mail_content = Column(Text, comment=u"邮件正文")
    job_id = Column(String(36), nullable=False, comment=u"apscheduler job id")
    recipients = Column(Text)
    deliver_as_group = Column(Boolean, default=True, comment=u"默认按组发送")
    delivery_type = Column(Enum(EmailDeliveryType))

    @renders('active')
    def is_active(self):
        return u"启用" if self.active else u"禁用"

    @renders('deliver_as_group')
    def is_deliver_as_group(self):
        return u"是" if self.deliver_as_group else u"否"

    @renders('slice_data')
    def is_slice_data(self):
        return u"是" if self.slice_data else u"否"

    @classmethod
    def get_instances(cls, ins_ids):
        instances = db.session.query(cls).filter(cls.id.in_(ins_ids))
        return instances

    @classmethod
    def get_instance_by_id(cls, ins_id):
        instance = db.session.query(cls).filter(cls.id == ins_id).first()
        return instance

    def delete_instance(self):
        db.session.delete(self)
        db.session.commit()

    def get_user_name(self, user_id):
        user = db.session.query(MyUser).filter(id == user_id).first()
        return user.username if user else ''

    def __unicode__(self):
        return self.name


class DashboardEmailSchedule(Model, AuditMixinNullable, EmailSchedule):
    """
    发送看板邮件
    """
    __tablename__ = 'dashboard_email_schedules'
    dashboard_id = Column(Integer, ForeignKey('dashboards.id'), nullable=False)
    dashboard = relationship(
        'Dashboard',
        backref=db.backref('email_schedules', cascade='all, delete-orphan'),
        foreign_keys=[dashboard_id]
    )

    @classmethod
    def get_list(cls):
        data = []
        if 'Admin' in g.user.roles:
            querys = db.session.query(cls)
        else:
            querys = db.session.query(cls).filter(cls.created_by_fk == g.user.id)

        for item in querys:
            info = {}
            info['name'] = item.name
            info['dashboard'] = item.dashboard.dashboard_title
            info['active'] = u"启用" if item.active else u"禁用"
            info['crontab'] = item.crontab
            info['creator'] = cls.get_user_name(item, item.created_by_fk)
            info['deliver_as_group'] = u"是" if item.deliver_as_group else u"否"
            info['delivery_type'] = item.delivery_type.value
            info['slice_data'] = u"是" if item.slice_data else u"否"
            data.append(info)
        return data


class SliceEmailSchedule(Model, AuditMixinNullable, EmailSchedule):

    __tablename__ = 'slice_email_schedules'
    slice_id = Column(Integer, ForeignKey('slices.id'), nullable=False)
    slice = relationship(
        'Slice',
        backref=db.backref('email_schedules', cascade='all, delete-orphan'),
        foreign_keys=[slice_id]
    )
    email_format = Column(Enum(SliceEmailReportFormat))

    @classmethod
    def get_list(cls):
        data = []
        if 'Admin' in g.user.roles:
            querys = db.session.query(cls)
        else:
            querys = db.session.query(cls).filter(cls.created_by_fk == g.user.id)

        for item in querys:
            info = {}
            info['name'] = item.name
            info['slice'] = item.slice.slice_name
            info['active'] = u"启用" if item.active else u"禁用"
            info['crontab'] = item.crontab
            info['creator'] = cls.get_user_name(item, item.created_by_fk)
            info['deliver_as_group'] = u"是" if item.deliver_as_group else u"否"
            info['delivery_type'] = item.delivery_type.value
            info['slice_data'] = item.slice_data
            info['email_format'] = item.email_format.value
            data.append(info)
        return data


def get_scheduler_model(report_type):
    if report_type == ScheduleType.dashboard.value:
        return DashboardEmailSchedule
    elif report_type == ScheduleType.slice.value:
        return SliceEmailSchedule