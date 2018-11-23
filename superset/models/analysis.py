# -*- coding:utf-8 -*-
# __author__ = majing
"""
在线分析模块
"""
import sqlalchemy as sqla

from flask_appbuilder.models.sqla import Model
from flask_appbuilder.models.decorators import renders
from sqlalchemy import Column, Integer, Text, String, UniqueConstraint, Table, ForeignKey
from sqlalchemy.orm import relationship

from superset import security_manager, db, ConnectorRegistry
from superset.models.helpers import AuditMixinNullable, ImportMixin
from superset.models.core import set_related_perm

metadata = Model.metadata


class SkModel(Model, AuditMixinNullable):
    """
    机器学习模型
    """
    __tablename__ = "sk_model"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), unique=True, nullable=False, comment=u"模型名字")
    full_name = Column(String(60), comment=u"模型中文名字")
    params = Column(Text, comment=u"模型的参数")

    def __repr__(self):
        return self.name


analysis_owner = Table('analysis_owner', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('analysis_id', Integer, ForeignKey('analysis.id')),
                    Column('user_id', Integer, ForeignKey('ab_user.id'))
)
analysis_show_user = Table('analysis_show_user', metadata,
                    Column('id', Integer, primary_key=True),
                    Column('analysis_id', Integer, ForeignKey('analysis.id')),
                    Column('user_id', Integer, ForeignKey('ab_user.id'))
)


class Analysis(Model, AuditMixinNullable):
    """
    分析模型
    """
    __tablename__ = "analysis"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(60), nullable=False, comment=u"分析模型的名字")
    version = Column(String(10), nullable=False, comment=u"分析模型的版本号")
    sk_model_id = Column(Integer, ForeignKey('sk_model.id'))
    sk_model = relationship(SkModel)
    datasource_id = Column(Integer, nullable=False, comment=u"资源ID")
    datasource_type = Column(String(20), nullable=False, default='table', comment=u"资源类型")
    datasource_name = Column(String(90), nullable=False, comment=u"资源名字")
    owner = relationship(security_manager.user_model, secondary=analysis_owner)
    show_user = relationship(security_manager.user_model, secondary=analysis_show_user)
    description = Column(Text, comment=u"分析模型描述")
    params = Column(Text, comment=u"模型参数")
    perm = Column(String(200), comment=u"权限")


    __table_args__ = (UniqueConstraint('name', 'version', name='_name_version'),
                      )

    def __repr__(self):
        return self.name

    @property
    def cls_model(self):
        return ConnectorRegistry.sources['table']

    @property
    def datasource(self):
        return self.get_datasource

    @property
    def get_datasource(self):
        return (
            db.session.query(self.cls_model)
                .filter_by(id=self.datasource_id)
                .first()
        )

    @renders("datasource_name")
    def datasource_link(self):
        datasource = self.datasource
        return datasource.link if datasource else None


sqla.event.listen(Analysis, 'before_insert', set_related_perm)
sqla.event.listen(Analysis, 'before_update', set_related_perm)
