# -*- coding:utf-8 -*-
# __author__ = majing
from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders

from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from superset import db

from ..collections.models import CollectRule
from ..validates.models import ValidateRule
from ..alarms.models import AlarmRule

from ..helpers import AuditMixinNullable
from ..base_models import BaseRecordModel


class PeriodTask(Model, AuditMixinNullable):
    """
    定时任务
    """
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False, unique=True, comment=u"任务名称")
    collect_rule_id = Column(Integer, ForeignKey('collect_rules.id'))
    collect_rule = relationship(CollectRule)
    validate_rule_id = Column(Integer, ForeignKey('validate_rules.id'))
    validate_rule = relationship(ValidateRule)
    alarm_rule_id = Column(Integer, ForeignKey('alarm_rules.id'))
    alarm_rule = relationship(AlarmRule)
    interval = Column(String(20), nullable=False, comment=u"定时任务时间间隔")
    status = Column(String(20), default='pending', nullable=False, comment=u"定时任务状态 pending|running|success|failed")
    detail = Column(Text, comment=u"任务详情")
    comment = Column(Text, comment=u"备注")

    def __str__(self):
        return self.name

    @classmethod
    def update_task_status_by_id(cls, task_id, status='running', detail='', session=None):
        session.query(PeriodTask).filter(PeriodTask.id == task_id).update({PeriodTask.status: status,
                                                                          PeriodTask.detail: detail
                                                                          })

    @classmethod
    def get_task_by_id(cls, task_id, session=None):
        return session.query(PeriodTask).filter(PeriodTask.id == task_id).first()


class TaskRecord(Model, BaseRecordModel):
    """
    定时任务运行记录
    """
    __tablename__ = 'task_record'

    duration = Column(Integer, comment=u"定时任务运行时间")

    @renders('duration')
    def exec_duration(self):
        return self.changed_on - self.created_on

    @classmethod
    def create_record_by_obj(cls, record, session=None):
        if isinstance(record, cls):
            session.add(record)


