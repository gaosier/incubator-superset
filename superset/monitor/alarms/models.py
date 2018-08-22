# -*- coding:utf-8 -*-
# __author__ = majing
import enum
from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders

from sqlalchemy import String, Column, Text, Integer, Boolean, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship

from superset import security_manager

from superset.monitor.helpers import AuditMixinNullable

from ..base_models import BaseRecordModel


alarm_users = Table('alarm_users', Model.metadata,
                    Column('id', Integer, primary_key=True),
                    Column('user_id', Integer, ForeignKey('ab_user.id')),
                    Column('alarm_id', Integer, ForeignKey('alarm_rules.id'))
                    )


class AlarmEnum(enum.Enum):
    email = 'email'
    phone = 'phone'


class AlarmRule(Model, AuditMixinNullable):
    __tablename__ = "alarm_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True, nullable=False)
    user = relationship(security_manager.user_model, secondary=alarm_users)
    alarm_type = Column(Enum(AlarmEnum))
    comment = Column(Text)

    def __str__(self):
        return self.name

    @renders('user')
    def usernames(self):
        return ','.join([user.username for user in self.user])


class AlarmRecord(Model, BaseRecordModel):
    __tablename__ = 'alarm_record'

    alarm_id = Column(Integer, comment=u"告警规则ID")
    alarm_name = Column(String(60), comment=u"告警规则名称")
    detail = Column(Text, comment=u"告警详情")

    def __str__(self):
        return self.alarm_name