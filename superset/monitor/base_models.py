# -*- coding:utf-8 -*-
# __author__ = majing
from sqlalchemy import Column, Integer, String, Text, Boolean

from superset.monitor.helpers import AuditMixinNullable


class BaseRecordModel(AuditMixinNullable):
    __tablename__ = None

    id = Column(Integer, primary_key=True)
    task_id = Column(Integer, nullable=False, comment=u"任务ID")
    task_name = Column(String(90), nullable=False, comment=u"任务名字")
    is_success = Column(Boolean, default=False, comment=u"运行结果")
    reason = Column(Text, comment=u"失败原因")
