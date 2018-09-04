# -*- coding:utf-8 -*-
# __author__ = majing
import json
from flask_appbuilder.models.sqla.interface import SQLAInterface

from superset import appbuilder
from .models import ValidateRule, ValidateErrorRule, ValidateRecord, ValidateFunc
from ..base import MonitorModelView, DeleteMixin
from ..base_filters import CommonFilter


class ValidateRuleModelView(MonitorModelView, DeleteMixin):
    """
    数据校验
    """
    datamodel = SQLAInterface(ValidateRule)

    list_title = '校验规则列表'
    show_title = '详情'
    add_title = '添加规则'
    edit_title = '编辑规则'

    search_columns = ('name', )
    list_columns = ['name', 'classify', 'is_multi_days_ft','comment', 'creator', 'modified']
    order_columns = ['name', 'modified']
    base_order = ('changed_on', 'desc')

    add_fieldsets = [
        ('共同配置',
         {"fields": ['name', 'classify', 'is_multi_days', 'start_time', 'end_time', 'comment']}
         ),
        (
            '函数类型',
            {'fields': ['pro_name', 'tab_name', 'fields', 'funcs', 'pt_format']}
        ),
        (
            'SQL语句',
            {'fields': ['sql_expression', 'funcs', 'min_compare_v', 'max_compare_v'], 'expanded': False}
        ),
        (
            '其他类型',
            {'fields': ['config', 'funcs'], 'expanded': False}
        ),
        (
            '汇总邮件',
            {'fields': ['funcs'], 'expanded': False}
        )
    ]

    edit_fieldsets = add_fieldsets
    show_fieldsets = add_fieldsets

    base_filters = [['id', CommonFilter, lambda: []]]

    label_columns = {
        'name': '规则名称',
        'creator': '创建者',
        'modified': '修改时间',
        'comment': '备注',
        'funcnames': '校验函数',
        'classify': '校验类别',
        'start_time': '开始时间',
        'end_time': '结束时间',
        'config': '配置信息',
        'pro_name': '项目名称',
        'tab_name': '表名',
        'fields': '字段',
        'funcs': '校验函数',
        'sql_expression': 'sql语句',
        'min_compare_v': '最小值',
        'max_compare_v': '最大值',
        'is_multi_days': '是否是多天',
        'pt_format': '分区信息',
        'is_multi_days_ft': '是否是多天'
    }

    description_columns = {
        "classify": "校验类型是必须字段.请选择与校验类别相同的分类,一次只能选择一个分类",
        "is_multi_days": "如果是True,请选择开始时间和结束时间；否则开始时间和结束时间不需要填写，默认是前一天的数据",
        "funcs": "必须选择和校验类别相同类型的校验函数"
    }

    def pre_add(self, item):
        if item.is_multi_days:
            if not item.start_time or not item.end_time:
                raise ValueError(u"添加规则失败：开始时间和结束时间必须选择")

    def pre_update(self, item):
        self.pre_add(item)


appbuilder.add_view(ValidateRuleModelView, 'ValidateRule',
    label='校验规则',
    icon='fa-book',
    category='Validate Manager',
    category_label='数据校验',
    category_icon='fa-cubes')


class ValidateRecordModelView(MonitorModelView, DeleteMixin):
    """
    校验记录
    """
    datamodel = SQLAInterface(ValidateRecord)

    base_permissions = ['can_list']

    list_title = '校验规则记录列表'

    search_columns = ('task_name', 'validate_rule_name', 'created_on')
    list_columns = ['task_name', 'validate_rule_name', 'operation', 'result', 'reason', 'created_on', 'changed_on']
    order_columns = ['task_name', 'created_on']
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'task_name': '任务名称',
        'validate_rule_name': '校验规则名称',
        'result': '校验结果',
        'reason': '失败详情',
        'created_on': '开始时间',
        'changed_on': '结束时间',
        'operation': '校验类型'
    }


appbuilder.add_view(ValidateRecordModelView, 'ValidateRecord',
                    label='校验记录',
                    icon='fa-list',
                    category='Validate Manager',
                    category_label='数据校验',
                    category_icon='fa-cubes')


class ValidateErrorRuleModelView(MonitorModelView, DeleteMixin):
    datamodel = SQLAInterface(ValidateErrorRule)

    list_title = '错误校验规则列表'
    show_title = '详情'
    add_title = '添加规则'
    edit_title = '编辑规则'

    search_columns = ('name', 'pro_name', 'table_name')
    list_columns = ['name', 'pro_name', 'table_name', 'rule', 'comment', 'creator', 'modified']
    order_columns = ['name', 'modified']
    edit_columns = ['name', 'pro_name', 'table_name', 'rule', 'comment']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')


    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'name': '规则名称',
        'pro_name': '项目名称',
        'table_name': '表名',
        'rule': '规则',
        'creator': '创建者',
        'modified': '修改时间',
        'comment': '备注',
    }

appbuilder.add_view(ValidateErrorRuleModelView, 'ValidateErrorRule',
                    label='错误校验规则',
                    icon='fa-bookmark',
                    category='Validate Manager',
                    category_label='数据校验',
                    category_icon='fa-cubes')


class ValidateTypeModelView(MonitorModelView, DeleteMixin):
    datamodel = SQLAInterface(ValidateFunc)

    list_title = '校验函数列表'
    show_title = '详情'
    add_title = '添加校验函数'
    edit_title = '编辑校验函数'

    search_columns = ('name', 'classify')
    list_columns = ['name', 'classify', 'comment', 'creator', 'modified']
    order_columns = ['name', 'modified']
    edit_columns = ['name', 'classify', 'comment']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'name': '函数名称',
        'creator': '创建者',
        'modified': '修改时间',
        'comment': '备注',
        'classify': '类型'
    }


appbuilder.add_view(ValidateTypeModelView, 'ValidateFunc',
                    label='校验函数',
                    icon='fa-anchor',
                    category='Validate Manager',
                    category_label='数据校验',
                    category_icon='fa-cubes')


