# -*- coding:utf-8 -*-
# __author__ = majing
from flask_appbuilder.models.sqla.interface import SQLAInterface

from superset import appbuilder
from .models import DataOriginConfig, MdConfig
from ..base import MonitorModelView, DeleteMixin
from ..base_filters import CommonFilter


class DataOriginConfigModelView(MonitorModelView, DeleteMixin):
    """
    数据源配置
    """
    datamodel = SQLAInterface(DataOriginConfig)

    list_title = '配置列表'
    show_title = '详情'
    add_title = '添加配置'
    edit_title = '编辑配置'

    search_columns = ('pro_name', 'db_name')
    list_columns = ['pro_name', 'db_name', 'comment', 'creator', 'modified']
    order_columns = ['pro_name', 'modified']
    edit_columns = ['pro_name', 'db_name', 'comment']
    add_columns = ['pro_name', 'db_name', 'comment']
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'pro_name': '项目名称',
        'creator': '创建者',
        'modified': '修改时间',
        'db_name': '数据库名字',
        'comment': '备注',
    }

appbuilder.add_view(DataOriginConfigModelView, 'OriginConfig',
    label='数据源配置',
    icon='fa-database',
    category='Global Config',
    category_label='全局配置',
    category_icon='fa-align-left')


class MdModelView(MonitorModelView, DeleteMixin):
    """
    埋点数据配置页面
    """
    datamodel = SQLAInterface(MdConfig)

    list_title = '配置列表'
    show_title = '详情'
    add_title = '添加配置'
    edit_title = '编辑配置'

    search_columns = ('pro_id', 'name')
    list_columns = ['pro_id','name', 'range', 'creator', 'modified']
    order_columns = ['pro_id', 'modified']
    edit_columns = ['pro_id', 'name', 'range', 'comment']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'pro_id': '项目ID',
        'name': '项目名称',
        'creator': '创建者',
        'modified': '修改时间',
        'range': '取值区间',
        'comment': '备注',
    }


appbuilder.add_view(MdModelView, 'MdConfig',
                    label='埋点配置',
                    icon='fa-briefcase',
                    category='Global Config',
                    category_label='全局配置',
                    category_icon='fa-align-left')
