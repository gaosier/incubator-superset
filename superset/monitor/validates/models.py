# -*- coding:utf-8 -*-
# __author__ = majing
import enum
import datetime
import json
import ast
import logging

from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders
from sqlalchemy import (String, Column, Text, Integer, Table, ForeignKey, UniqueConstraint, Enum,
                        DateTime, Boolean)
from sqlalchemy.orm import relationship

from superset.monitor.helpers import AuditMixinNullable

from ..base_models import BaseRecordModel

validate_rule_types = Table('validate_rule_funcs', Model.metadata,
                            Column('id', Integer, primary_key=True),
                            Column('rule_id', Integer, ForeignKey('validate_rules.id')),
                            Column('func_id', Integer, ForeignKey('validate_funcs.id'))
                            )


class ValidateEnum(enum.Enum):
    func = '函数'
    sql = 'sql语句'
    other = '其他'


class ValidateFunc(Model, AuditMixinNullable):
    __tablename__ = "validate_funcs"
    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True, nullable=False)
    classify = Column(Enum(ValidateEnum), default='func', nullable=False)
    comment = Column(Text)

    def __str__(self):
        return self.name


class ValidateRule(Model, AuditMixinNullable):
    __tablename__ = "validate_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(60), unique=True, nullable=False)
    classify = Column(Enum(ValidateEnum), default='func', nullable=False)
    pro_name = Column(String(60))
    tab_name = Column(String(60))
    fields = Column(Text, default="{}")
    funcs = relationship("ValidateFunc", secondary=validate_rule_types)
    sql_expression = Column(Text)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    compare_v = Column(Integer, default=1)
    config = Column(Text)
    comment = Column(Text)
    is_multi_days = Column(Boolean, default=False)
    pt_format = Column(String(60), default='pt=%Y%m%d')

    def __str__(self):
        return self.name

    @renders('funcs')
    def funcnames(self):
        return ','.join([item.name for item in self.funcs])

    @renders('is_multi_days')
    def is_multi_days_ft(self):
        return '是' if self.is_multi_days else '否'

    @classmethod
    def get_validate_rule_by_id(cls, rule_id, session=None):
        return session.query(cls).filter(cls.id == rule_id).first()

    @property
    def columns(self):
        field_infos = {}
        if self.classify is ValidateEnum.func:
            try:
                field_infos = ast.literal_eval(self.fields)
            except Exception as exc:
                logging.error("get all fields error: %s" % str(exc))
                field_infos = json.loads(self.fields)
        return field_infos

    @property
    def all_fields(self):
        cols = []
        for val in self.columns.values():
            cols.extend(val)
        return list(set(cols))

    @property
    def repeat_fields(self):
        return self.columns.get('repeat', [])

    @property
    def error_fields(self):
        return self.columns.get('error', [])

    @property
    def missing_fields(self):
        return self.columns.get('missing', [])

    def get_partitions(self, key, fmt, symbol='='):
        pts = []
        start_time = self.start_time
        if self.is_multi_days:
            while start_time <= self.end_time:
                _format = start_time.strftime(fmt)
                if symbol == '>=':
                    _en_time = (start_time + datetime.timedelta(days=1)).strftime(fmt)
                    pt = "(%s>='%s' and %s<'%s')" % (key, _format, key, _en_time)
                else:
                    pt = "%s%s%s" % (key, symbol, _format)
                pts.append(pt)
                start_time = start_time + datetime.timedelta(days=1)
        else:
            _format = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(fmt)
            if symbol == '>=':
                _en_time = datetime.datetime.now().strftime(fmt)
                pt = "(%s>='%s' and %s<'%s')" % (key, _format, key, _en_time)
            else:
                pt = "%s%s%s" % (key, symbol, _format)
            pts.append(pt)
        return pts

    @property
    def partition(self):
        result = []
        if self.classify is ValidateEnum.func and self.pt_format:
            if ">=" not in self.pt_format:
                values = self.pt_format.split('=')
                symbol = "="
            else:
                values = self.pt_format.split(">=")
                symbol = ">="
            if len(values) == 2:
                name, _format = values
                result = self.get_partitions(name, _format, symbol=symbol)
        return result


class ValidateErrorRule(Model, AuditMixinNullable):
    __tablename__ = 'validate_error_rule'

    id = Column(Integer, primary_key=True)
    name = Column(String(60), nullable=False)
    pro_name = Column(String(60), nullable=False)
    table_name = Column(String(60), nullable=False)
    rule = Column(Text)
    compare_v = Column(Integer, default=1, nullable=False, comment=u"阈值")
    comment = Column(Text)

    __table_args__ = (UniqueConstraint('pro_name', 'table_name', name='project_table_name_uc'),
                      )

    def __str__(self):
        return self.name

    @classmethod
    def get_table_error_conf(cls, pro_name, tab_name, session):
        return session.query(cls).filter(cls.pro_name == pro_name, cls.table_name == tab_name).first()


class ValidateRecord(Model, BaseRecordModel):
    __tablename__ = 'validate_record'

    validate_rule_id = Column(Integer, comment=u"校验规则ID")
    validate_rule_name = Column(String(60), comment=u"校验规则名称")
    operation = Column(String(60), comment=u"具体的校验操作")

    def __str__(self):
        return self.validate_rule_name

    @renders('is_success')
    def result(self):
        return u'是' if self.is_success else u'否'

    @classmethod
    def get_records_by_id(cls, record_id, session=None):
        return session.query(cls).filter(cls.id == record_id).first()