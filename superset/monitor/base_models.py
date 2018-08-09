# -*- coding:utf-8 -*-
# __author__ = majing
from sqlalchemy import Column, Integer, String, Text, Boolean
from flask_appbuilder.models.decorators import renders

from superset.monitor.helpers import AuditMixinNullable


class BaseRecordModel(AuditMixinNullable):
    __tablename__ = None

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, nullable=False, comment=u"任务ID")
    task_name = Column(String(90), nullable=False, comment=u"任务名字")
    is_success = Column(Boolean, default=False, comment=u"运行结果")
    reason = Column(Text, comment=u"失败原因")

    @classmethod
    def add_task_record(cls, session=None, **kwargs):
        try:
            if kwargs.get('task_id') and kwargs.get('task_name'):
                task = cls(**kwargs)
                session.add(task)
        except Exception as exc:
            raise ValueError("add_taks_record error: %s" % str(exc))

    @renders('is_success')
    def result(self):
        return u"成功" if self.is_success else u"失败"


