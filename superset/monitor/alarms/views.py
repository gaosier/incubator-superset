# -*- coding:utf-8 -*-
# __author__ = majing

from flask_appbuilder.models.sqla.interface import SQLAInterface

from superset import appbuilder
from .models import AlarmRule, AlarmRecord
from ..base import MonitorModelView, DeleteMixin
from ..base_filters import CommonFilter


class AlarmModelView(MonitorModelView, DeleteMixin):
    """
    告警规则
    """
    datamodel = SQLAInterface(AlarmRule)

    list_title = '告警规则列表'
    show_title = '详情'
    add_title = '添加规则'
    edit_title = '编辑规则'

    search_columns = ('name', 'user')
    list_columns = ['name', 'usernames', 'alarm_type', 'comment', 'creator', 'modified']
    order_columns = ['name', 'modified']
    edit_columns = ['name', 'user', 'alarm_type', 'comment']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'name': '规则名称',
        'alarm_type': '告警类型',
        'user': '告警用户',
        'creator': '创建者',
        'modified': '修改时间',
        'comment': '备注',
        'usernames': '告警用户',
    }

appbuilder.add_view(AlarmModelView, 'AlarmRule',
    label='告警规则',
    icon='fa-building',
    category='Alarm Manager',
    category_label='告警管理',
    category_icon='fa-bell')


class AlarmRecordModelView(MonitorModelView, DeleteMixin):
    """
    数据源配置
    """
    datamodel = SQLAInterface(AlarmRecord)

    base_permissions = ['can_list']

    list_title = '告警规则记录列表'

    search_columns = ('task_name', 'alarm_name', 'created_on')
    list_columns = ['task_name', 'alarm_name', 'result', 'reason', 'created_on']
    order_columns = ['task_name', 'created_on']
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'task_name': '任务名称',
        'alarm_name': '告警规则名称',
        'result': '告警结果',
        'reason': '失败详情',
        'detail': '告警详情',
        'created_on': '告警时间',
        'changed_on': '结束时间',
    }

appbuilder.add_view(AlarmRecordModelView, 'AlarmRecord',
    label='告警记录',
    icon='fa-list',
    category='Alarm Manager',
    category_label='告警管理',
    category_icon='fa-bell]')