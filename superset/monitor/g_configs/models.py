# -*- coding:utf-8 -*-
# __author__ = majing

from flask_appbuilder import Model
from sqlalchemy import (
    Column, Integer,
    String, Text,
)

from superset.monitor.helpers import AuditMixinNullable


class DataOriginConfig(Model, AuditMixinNullable):
    """
    数据源配置表
    """
    __tablename__ = "data_origin_config"

    id = Column(Integer, primary_key=True)
    pro_name = Column(String(50), comment=u"项目名称")
    db_name = Column(String(50), comment=u"数据库名称")
    comment = Column(Text, comment=u"备注")


class MdConfig(Model, AuditMixinNullable):
    """
    埋点数据量配置表
    """
    __tablename__ = 'md_config'

    id = Column(Integer, primary_key=True)
    pro_id = Column(String(20), comment=u"项目ID")
    name = Column(String(50), comment=u"项目名称")
    range = Column(String(90), default='[]', comment=u"取值区间")
    comment = Column(Text, comment=u"备注")