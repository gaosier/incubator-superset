# -*- coding:utf-8 -*-
# __author__ = majing
import json
import datetime

from flask_appbuilder import Model
from sqlalchemy import Column, Integer,String, Text, DateTime

from superset.monitor.helpers import AuditMixinNullable
from superset import  db

from ..base_models import BaseRecordModel


class CollectRule(Model, AuditMixinNullable):
    """
    数据源配置表
    """
    __tablename__ = "collect_rules"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, unique=True, comment=u"规则名称")
    rule_type = Column(String(20), nullable=False, default='tb', comment=u"tb(表) | db(数据库)")
    pro_name = Column(String(50), comment=u"项目名称")
    table_name = Column(String(50), comment=u"表名称")
    fields = Column(Text, comment=u"需要采集数据的字段")
    collect_day = Column(DateTime, comment=u"采集日期")
    partion_format = Column(String(60), default="pt=%Y%m%d", comment=u"分区格式")
    sql_expression = Column(String(225), comment=u"sql语句")
    comment = Column(Text, comment=u"备注")

    def __str__(self):
        return self.name

    @classmethod
    def get_model_by_id(cls, id):
        session = db.session
        return session.query(cls).filter_by(id=id).first()

    @property
    def columns(self):
        return json.loads(self.fields)

    @property
    def all_fields(self):
        cols = []
        for val in self.columns.values():
            cols.extend(val)
        return list(set(cols))

    @property
    def repeat_fields(self):
        columns = json.loads(self.fields) or {}
        return columns.get('repeat')

    @property
    def error_fields(self):
        columns = json.loads(self.fields) or {}
        return columns.get('error')

    @property
    def missing_fields(self):
        columns = json.loads(self.fields) or {}
        return columns.get('error')

    @property
    def partition(self):
        result = None
        if self.partion_format:
            values = self.partion_format.split('=')
            if len(values) == 2:
                name, _format = values
                if not self.collect_day:
                    day = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime(_format)
                else:
                    day = self.collect_day.strftime(_format)
                result = "%s=%s" % (name, day)
        return result


class CollectRecord(Model, BaseRecordModel):
    """
    采集记录
    """
    __tablename__ = 'collect_record'

    collect_rule_id = Column(Integer, comment=u"采集规则ID")
    collect_rule_name = Column(String(60), comment=u"采集规则名称")




