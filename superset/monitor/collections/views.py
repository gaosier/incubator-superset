# -*- coding:utf-8 -*-
# __author__ = majing
from flask_appbuilder.models.sqla.interface import SQLAInterface

from superset import appbuilder
from .models import CollectRule, CollectRecord
from ..base import MonitorModelView, DeleteMixin
from ..base_filters import CommonFilter
from ..funcs import CollectInter


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
    edit_columns = ['name', 'rule_type', 'pro_name', 'table_name', 'fields', 'collect_day', 'partion_format',
                    'comment']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'name': '规则名称',
        'rule_type': '规则类型',
        'pro_name': '项目名称',
        'table_name': '表名',
        'fields': '采集字段',
        'collect_day': '采集日期',
        'creator': '创建者',
        'modified': '修改时间',
        'comment': '备注',
        'partion_format': '分区格式'
    }

    description_columns = {
        "rule_type": "db(数据库)| tb(表)两种类型；如果是db类型,后面的选项可以不用填",
        "fields": "{'repeat': ['name'], 'missing': ['id'], 'error': [], 'count': []}",
        "partion_format": "如果规则类型是tb, 分区类型必须填写",
        "collect_day": "如果不填，默认采集前一天的数据"
    }


appbuilder.add_view(CollectRuleModelView, 'CollectRule',
    label='采集规则',
    icon='fa-industry',
    category='Collect Manager',
    category_label='数据采集',
    category_icon='fa-folder-open')


class CollectRecordModelView(MonitorModelView, DeleteMixin):
    """
    采集记录
    """
    datamodel = SQLAInterface(CollectRecord)

    base_permissions = ['can_list']

    list_title = '采集规则记录列表'

    search_columns = ('task_name', 'collect_rule_name', 'created_on')
    list_columns = ['task_name', 'collect_rule_name', 'result', 'reason', 'created_on', 'changed_on']
    order_columns = ['task_name', 'created_on']
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'task_name': '任务名称',
        'collect_rule_name': '采集规则名称',
        'result': '采集结果',
        'reason': '失败详情',
        'fields': '采集字段',
        'created_on': '开始时间',
        'changed_on': '结束时间',
    }


appbuilder.add_view(CollectRecordModelView, 'CollectRecord',
                    label='规则记录',
                    icon='fa-list',
                    category='Collect Manager',
                    category_label='数据采集',
                    category_icon='fa-folder-open')


