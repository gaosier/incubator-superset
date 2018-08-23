# -*- coding:utf-8 -*-
# __author__ = majing
import time
import json
from concurrent.futures import ProcessPoolExecutor

from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders

from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, func
from sqlalchemy.orm import relationship
import sqlalchemy as sqla

from superset import db

from ..collections.models import CollectRule
from ..validates.models import ValidateRule
from ..alarms.models import AlarmRule

from ..helpers import AuditMixinNullable
from ..base_models import BaseRecordModel
from ..utils import get_celery_beat_worker_pid, pkill_celery, restart_celery_beat, restart_celery_worker


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
    is_active = Column(Boolean, default=True, comment=u"禁用启用")

    def __str__(self):
        return self.name

    @classmethod
    def update_task_status_by_id(cls, task_id, status='running', detail='', session=None):
        session.query(PeriodTask).filter(PeriodTask.id == task_id).update({PeriodTask.status: status,
                                                                          PeriodTask.detail: detail
                                                                          })
        session.commit()

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
            session.commit()

    @classmethod
    def get_task_record_by_id(cls, record_id, session=None):
        return session.query(cls).filter(cls.id == record_id).first()

    @classmethod
    def update_record_by_id(cls, record_id, is_success=None, detail='', session=None):
        session.query(cls).filter(cls.id == record_id).update({cls.is_success: is_success, cls.reason: detail})
        session.commit()


class CeleryRestartRecord(Model, BaseRecordModel):
    """
    重启celery记录表
    """
    __tablename__ = "celery_restart_rds"

    operation = Column(String(20), comment=u"操作")
    old_pids = Column(String(100), comment=u"旧的进程号")
    cur_pids = Column(String(100), comment=u"当前进程号")
    status = Column(String(20), default='running', comment=u"running|complete")
    is_restart = Column(String(10), default='undefined', comment=u"undefined|success|failed")

    @renders('is_restart')
    def restarts(self):
        if self.is_restart == 'undefined':
            return u"未知"
        elif self.is_restart == 'success':
            return u"成功"
        else:
            return u"失败"


def async_restart_celery(mapper, connection, target):
    """
    :param task_id: 
    :param task_name: 
    :param operation:  
    """
    session = db.create_scoped_session()
    old_pids = get_celery_beat_worker_pid()

    count = 0       #
    while session.query(func.count(PeriodTask.id)).filter(PeriodTask.status == 'running').scalar() > 0:
        time.sleep(60)
        count += 1

        if count == 10:
            break

    CeleryRestartRecord.add_task_record(task_id=target.id, task_name=target.name, is_restart="undefined", reason='',
                                        old_pids=json.dumps(old_pids), session=session)
    session.commit()
    session.close()

    pkill_celery()

    with ProcessPoolExecutor(2) as executor:
        executor.submit(restart_celery_beat)
        executor.submit(restart_celery_worker)


sqla.event.listen(PeriodTask, 'after_insert', async_restart_celery)
sqla.event.listen(PeriodTask, 'after_update', async_restart_celery)
sqla.event.listen(CollectRule, 'after_update', async_restart_celery)
sqla.event.listen(AlarmRule, 'after_update', async_restart_celery)
sqla.event.listen(ValidateRule, 'after_update', async_restart_celery)