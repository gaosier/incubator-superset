# -*- coding:utf-8 -*-
# __author__ = majing

from flask_appbuilder.models.sqla.interface import SQLAInterface

from superset import appbuilder
from .models import ValidateRule, ValidateErrorRule, ValidateRecord, ValidateType
from ..base import MonitorModelView, DeleteMixin
from ..base_filters import CommonFilter
from ..funcs import CollectInter


class ValidateRuleModelView(MonitorModelView, DeleteMixin):
    """
    数据校验
    """
    datamodel = SQLAInterface(ValidateRule)

    list_title = '校验规则列表'
    show_title = '详情'
    add_title = '添加规则'
    edit_title = '编辑规则'

    search_columns = ('types', 'name')
    list_columns = ['name', 'typenames', 'comment', 'creator', 'modified']
    order_columns = ['name', 'modified']
    edit_columns = ['name', 'types', 'comment']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'name': '规则名称',
        'types': '校验类型',
        'creator': '创建者',
        'modified': '修改时间',
        'comment': '备注',
        'typenames': '校验类型',
    }


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
                    label='规则记录',
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

    def post_update(self, item):
        CollectInter.collect_tb_data(1, '测试任务', item)


appbuilder.add_view(ValidateErrorRuleModelView, 'ValidateErrorRule',
                    label='错误校验规则',
                    icon='fa-bookmark',
                    category='Validate Manager',
                    category_label='数据校验',
                    category_icon='fa-cubes')


class ValidateTypeModelView(MonitorModelView, DeleteMixin):
    datamodel = SQLAInterface(ValidateType)

    list_title = '校验规则类型列表'
    show_title = '详情'
    add_title = '添加规则'
    edit_title = '编辑规则'

    search_columns = ('name', )
    list_columns = ['name', 'comment', 'creator', 'modified']
    order_columns = ['name', 'modified']
    edit_columns = ['name', 'comment']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'name': '规则名称',
        'creator': '创建者',
        'modified': '修改时间',
        'comment': '备注',
    }


appbuilder.add_view(ValidateTypeModelView, 'ValidateType',
                    label='校验类型',
                    icon='fa-anchor',
                    category='Validate Manager',
                    category_label='数据校验',
                    category_icon='fa-cubes')


