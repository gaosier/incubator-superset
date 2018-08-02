# -*- coding:utf-8 -*-
# __author__ = majing

from flask_appbuilder.models.sqla.interface import SQLAInterface

from superset import appbuilder
from .models import CollectRule
from ..base import MonitorModelView, DeleteMixin
from ..base_filters import CommonFilter


class CollectRuleModelView(MonitorModelView, DeleteMixin):
    """
    数据源配置
    """
    datamodel = SQLAInterface(CollectRule)

    list_title = '采集规则列表'
    show_title = '详情'
    add_title = '添加规则'
    edit_title = '编辑规则'

    search_columns = ('rule_type', 'pro_name', 'table_name')
    list_columns = ['name', 'rule_type', 'pro_name', 'table_name', 'fields', 'comment', 'creator', 'modified']
    order_columns = ['pro_name', 'modified']
    edit_columns = ['name', 'rule_type', 'pro_name', 'table_name', 'fields', 'start_time', 'end_time', 'comment']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'name': '规则名称',
        'rule_type': '规则类型',
        'pro_name': '项目名称',
        'table_name': '表名',
        'fields': '采集字段',
        'start_time': '开始时间',
        'end_time': '结束时间',
        'creator': '创建者',
        'modified': '修改时间',
        'db_name': '数据库名字',
        'comment': '备注',
    }

appbuilder.add_view(CollectRuleModelView, 'CollectRule',
    label='采集规则',
    icon='fa-industry',
    category='Collect Manager',
    category_label='数据采集',
    category_icon='fa-folder-open')