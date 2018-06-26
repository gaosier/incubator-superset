from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from copy import copy, deepcopy
from datetime import date, datetime
import functools
import json
import logging
import textwrap

from flask import escape, g, Markup, request
from flask_appbuilder import Model
from flask_appbuilder.models.decorators import renders
from future.standard_library import install_aliases
import numpy
import pandas as pd
import sqlalchemy as sqla
from sqlalchemy import (
    Boolean, Column, create_engine, Date, DateTime, ForeignKey, Integer,
    MetaData, select, String, Table, Text,SmallInteger
)
from sqlalchemy.engine import url
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import relationship, subqueryload
from sqlalchemy.orm.session import make_transient
from sqlalchemy.pool import NullPool
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.sql import text
from sqlalchemy.sql.expression import TextAsFrom
from sqlalchemy_utils import EncryptedType

from superset import app, db, db_engine_specs, security_manager, utils
from superset.connectors.connector_registry import ConnectorRegistry
from superset.models.helpers import AuditMixinNullable, ImportMixin, set_perm
from superset.viz import viz_types
install_aliases()
from urllib import parse  # noqa

config = app.config
custom_password_store = config.get('SQLALCHEMY_CUSTOM_PASSWORD_STORE')
stats_logger = config.get('STATS_LOGGER')
metadata = Model.metadata  # pylint: disable=no-member


class JingYouUser(Model):
    __tablename__ = 'jingyou_user'  # {connector_name}_column

    uname = Column(String(64), primary_key=True,nullable=False)
    password = Column(String(64),nullable=True)
    ua = Column(Text)
    cookies = Column(Text)
    ip = Column(String(64),nullable=True)
    port = Column(SmallInteger, nullable=True)
    comment=Column(String(255),nullable=True)
    updated = Column(
        DateTime, default=datetime.now,
        onupdate=datetime.now, nullable=True)
    status = Column(SmallInteger, default=1,nullable=False)
    subject_product=Column(String(255),nullable=True)

    @property
    def get_status(self):
        str_btn = ''
        if self.status == 1:
            str_btn = '<button type="button" class="btn btn-primary btn-xs">正常</button>'
        elif self.status == 2:
            str_btn = '<button type="button" class="btn btn-xs">修复中</button>'
        elif self.status == 3:
            str_btn = '<button type="button" class="btn btn-danger btn-xs">异常</button>'
        return str_btn


class MProject(Model):
    __tablename__='m_project'
    id=Column(String(32),primary_key=True,nullable=False)
    name=Column(String(64),nullable=True)
    full_id=Column(String(64),nullable=True)
    describe=Column('m_describe',String(255),nullable=True)
    pm_owner=Column(String(64),nullable=True)
    tech_owner=Column(String(64),nullable=True)
    status = Column(Boolean, default=False)
    create_time = Column(DateTime, default=datetime.now, nullable=True)
    update_time = Column(
        DateTime, default=datetime.now,
        onupdate=datetime.now, nullable=True)
    name_type=Column(String(64),nullable=True)
    ## m_page=relationship('MPage',back_populates="m_project")
    def __repr__(self):
        return self.name
    @property
    def page_or_element_button(self):
        params = '_flt_0_m_project=%s' % self.id
        url1 = "/mpageview/list/?{params}".format(params=params)
        return Markup("<center>\
        <div class='btn-group btn-group-xs' style='display: flex;'>\
        <a href={url1} class='btn btn-sm btn-default' data-toggle='tooltip' rel='tooltip' title='' data-original-title='该项目的页面埋点'>页面埋点</a>\
        </div></center>".format(url1=url1))

    def base_link(self,params=None):
        if not params:
            params='_flt_0_m_project=%s'%self.id
            name = escape(self.name)
        else:
            name=escape(self.name_type)
        url = (
            "/mpageview/list/?{params}".format(params=params))
        return Markup('<a href="{url}">{name}</a>'.format(**locals()))

    @property
    def get_status(self):
        str_btn = ''
        if not self.status :
            str_btn = '<a type="button" class="btn btn-primary disabled btn-xs">正常</a>'
        else:
            str_btn = '<a type="button" class="btn btn-danger disabled btn-xs">禁用</a>'
        return str_btn

    @property
    def project_link(self):
        return self.base_link()

    @property
    def project_type_link(self):
        mproject_list=db.session.query(MProject).filter_by(name_type=self.name_type)
        params=''
        for i in mproject_list:
            params+='_flt_0_m_project=%s&'%i.id
        return self.base_link(params=params)

    @property
    def element_link(self):
        return Markup('<a href="{url}">{url}</a>'.format(url='/melementview/list/'))


mpage_mproject = Table(
    'mpage_mproject', metadata,
    Column('id', Integer, primary_key=True),
    Column('mproject_id', String(32), ForeignKey('m_project.id')),
    Column('mpage_id', Integer, ForeignKey('m_page.id')),
)
class MpageMproject(Model):
    __tablename__ = 'mpage_mproject'

    id=Column(Integer, primary_key=True,nullable=False)
    mproject_id=Column(String(32),ForeignKey('m_project.id'),nullable=False)
    mpage_id=Column(Integer,ForeignKey('m_page.id'),nullable=False,)
    mpage=relationship('MPage')
    mproject=relationship('MProject')

    def __repr__(self):
        return '%s-%s'%(self.mproject.name,self.mpage.page_id)

melement_mpage_mproject=Table(
    'melement_mpage_mproject', metadata,
    Column('id', Integer, primary_key=True),
    Column('melement_id', Integer, ForeignKey('m_element.id')),
    Column('mpage_mproject_id', Integer, ForeignKey('mpage_mproject.id')),
)

class MPage(Model):
    __tablename__='m_page'

    id=Column(Integer, primary_key=True,nullable=False)
    page_id=Column(String(64),nullable=False)
    m_project = relationship(
        'MProject', secondary=mpage_mproject)
    menu1=Column(String(64),nullable=True)
    menu2=Column(String(64),nullable=True)
    menu3=Column(String(64),nullable=True)
    menu4=Column(String(64),nullable=True)
    name=Column(String(64),nullable=False)
    status = Column(Boolean, default=False)
    del_status = Column(Boolean, default=False)
    url = Column(String(2048), nullable=True)
    m_describe = Column(String(255), nullable=True)
    up1 = Column(String(1024), nullable=True)
    up2 = Column(String(1024), nullable=True)
    up3 = Column(String(1024), nullable=True)
    up4 = Column(String(1024), nullable=True)
    up5 = Column(String(1024), nullable=True)
    pp1 = Column(String(1024), nullable=True)
    pp2 = Column(String(1024), nullable=True)
    pp3 = Column(String(1024), nullable=True)
    pp4 = Column(String(1024), nullable=True)
    pp5 = Column(String(1024), nullable=True)
    tag = Column(String(255), nullable=True)
    m_process = Column(Integer, default=1, nullable=False)
    version = Column(SmallInteger, default=1, nullable=False)
    create_time = Column(DateTime, default=datetime.now, nullable=True)
    update_time = Column(
        DateTime, default=datetime.now,
        onupdate=datetime.now, nullable=True)
    melement_url = Column(String(2048), nullable=True)

    # @property
    # def element_link(self):
    #     url = self.melementview_url()
    #     if not url:
    #         return ''
    #     else:
    #         return url
    @property
    def melement_url_btn(self):
        url=self.melement_url
        if not url:
            return Markup("<center>\
                        <div class='btn-group btn-group-xs' style='display: flex;'>\
                            <a href={url1} class='btn btn-sm btn-default' data-toggle='tooltip' rel='tooltip' title='' data-original-title='该页面的点击埋点'>添加</a>\
                                    </div></center>".format(url1='/melementview/add'))
        return Markup("<center>\
            <div class='btn-group btn-group-xs' style='display: flex;'>\
                <a href={url1} class='btn btn-sm btn-default' data-toggle='tooltip' rel='tooltip' title='' data-original-title='该页面的点击埋点'>点击行为</a>\
                        </div></center>".format(url1=url))

    # def melementview_url(self):
    #     mpage_mproject_list = db.session.query(MpageMproject).filter_by(mpage_id=self.id)
    #     url = '/melementview/list/?'
    #     flag=False
    #     for i in mpage_mproject_list:
    #         url += '_flt_0_mpage_mproject=%s&' % i.id
    #         if not flag:
    #             if len(db.session.query(MElement).filter(MElement.mpage_mproject.contains(i)).all())!= 0:
    #                 flag=True
    #     if flag:
    #         return url
    #     else:
    #         return None

    @property
    def get_del_status(self):
        if self.del_status == False:
            str_btn = '<a type="button" class="btn btn-primary btn-xs disabled">正常</a>'
        else:
            str_btn = '<a class="btn btn-danger btn-xs disabled">已删除</a>'
        return str_btn
    # __table_args__ = (
    #     UniqueConstraint('page_id','project_id'),
    # )
    @property
    def get_status(self):
        if not self.status:
            str_btn = '<button type="button" class="btn btn-default btn-xs">未修改</button>'
        else:
            str_btn = '<button type="button" class="btn btn-info btn-xs">已修改</button>'
        return str_btn

    @property
    def mproject_name(self):
        st = ''
        for i in self.m_project:
            st+='<div>%s</div>'%(str(i))
        return st

class MElement(Model):
    __tablename__ = 'm_element'

    id = Column(Integer, primary_key=True, nullable=False)
    element_id = Column(String(64), nullable=False)
    mpage_mproject = relationship(
        'MpageMproject', secondary=melement_mpage_mproject)
    name = Column(String(64), nullable=False)
    status = Column(Boolean, default=False)
    del_status = Column(Boolean, default=False)
    pp1 = Column(String(1024), nullable=True)
    pp2 = Column(String(1024), nullable=True)
    pp3 = Column(String(1024), nullable=True)
    pp4 = Column(String(1024), nullable=True)
    pp5 = Column(String(1024), nullable=True)
    tag = Column(String(255), nullable=True)
    m_process = Column(Integer, default=1, nullable=False)
    version = Column(SmallInteger, default=1, nullable=False)
    create_time = Column(DateTime, default=datetime.now, nullable=True)
    update_time = Column(
        DateTime, default=datetime.now,
        onupdate=datetime.now, nullable=True)

    @property
    def mproject(self):
        return [ i.mproject_id for i in self.mpage_mproject]

    @property
    def mpage(self):
        return [ i.mpage.page_id for i in self.mpage_mproject]

    @property
    def get_status(self):
        if not self.status:
            str_btn = '<button type="button" class="btn btn-default btn-xs">未修改</button>'
        else:
            str_btn = '<button type="button" class="btn btn-info btn-xs">已修改</button>'
        return str_btn

    @property
    def get_del_status(self):
        if self.del_status == False:
            str_btn = '<a type="button" class="btn btn-primary btn-xs disabled">正常</a>'
        else:
            str_btn = '<a type="button" class="btn btn-danger btn-xs disabled">已删除</a>'
        return str_btn

    @property
    def mpage_mproject_name(self):
        st=''
        for i in self.mpage_mproject:
            st+='<div>%s</div>'%(str(i))
        return st