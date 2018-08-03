# -*- coding:utf-8 -*-
# __author__ = majing

from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders
from sqlalchemy import Column, Integer,String, Text, DateTime

from superset.monitor.helpers import AuditMixinNullable

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
    start_time = Column(DateTime, comment=u"开始时间")
    end_time = Column(DateTime, comment=u"结束时间")
    comment = Column(Text, comment=u"备注")


class CollectRecord(Model, BaseRecordModel):
    """
    采集记录
    """
    __tablename__ = 'collect_record'

    collect_rule_id = Column(Integer, comment=u"采集规则ID")
    collect_rule_name = Column(String(60), comment=u"采集规则名称")

    @renders('is_success')
    def result(self):
        return u"成功" if self.is_success else u"失败"




