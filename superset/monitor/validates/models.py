# -*- coding:utf-8 -*-
# __author__ = majing
from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders
from sqlalchemy import String, Column, Text, Integer, Boolean, Table, ForeignKey
from sqlalchemy.orm import relationship

from superset.monitor.helpers import AuditMixinNullable

from ..base_models import BaseRecordModel

validate_rule_types = Table('validate_rule_types', Model.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('rule_id', Integer, ForeignKey('validate_rules.id')),
                            Column('type_id', Integer, ForeignKey('validate_types.id'))
                            )


class ValidateType(Model, AuditMixinNullable):
    __tablename__ = "validate_types"
    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True, nullable=False)
    comment = Column(Text)

    def __str__(self):
        return self.name


class ValidateRule(Model, AuditMixinNullable):
    __tablename__ = "validate_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True, nullable=False)
    types = relationship("ValidateType", secondary=validate_rule_types)
    comment = Column(Text)

    def __str__(self):
        return self.name

    @renders('types')
    def typenames(self):
        print("typenames: ", ','.join([item.name for item in self.types]))
        return ','.join([item.name for item in self.types])


class ValidateErrorRule(Model, AuditMixinNullable):
    __tablename__ = 'validate_error_rule'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    pro_name = Column(String(60), nullable=False)
    table_name = Column(String(60), nullable=False)
    rule = Column(Text)
    comment = Column(Text)

    def __str__(self):
        return self.name


class ValidateRecord(Model, BaseRecordModel):
    __tablename__ = 'validate_record'

    validate_rule_id = Column(Integer, comment=u"校验规则ID")
    validate_rule_name = Column(String(60), comment=u"校验规则名称")

    def __str__(self):
        return self.validate_rule_name