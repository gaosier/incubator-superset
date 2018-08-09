# -*- coding:utf-8 -*-
# __author__ = majing
"""
contab: * * * * * 
* 分钟   * 小时  * 天    * 月份   * 星期
"""
from flask_appbuilder.models.sqla.interface import SQLAInterface

from superset import appbuilder

from ..base import MonitorModelView
from ..base_filters import CommonFilter

from .models import PeriodTask, TaskRecord


class TaskModelView(MonitorModelView):
    datamodel = SQLAInterface(PeriodTask)

    list_title = '任务列表'
    show_title = '详情'
    add_title = '添加任务'
    edit_title = '编辑任务'

    search_columns = ('name', 'status')
    list_columns = ['name', 'collect_rule', 'validate_rule', 'alarm_rule', 'interval', 'status', 'detail', 'modified']
    order_columns = ['name', 'modified']
    edit_columns = ['name', 'collect_rule', 'validate_rule', 'alarm_rule', 'interval', 'status', 'comment']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'name': '任务名称',
        'creator': '创建者',
        'modified': '修改时间',
        'collect_rule': '采集规则',
        'validate_rule': '校验规则',
        'alarm_rule': '告警规则',
        'comment': '备注',
        'interval': '时间间隔',
        'status': '任务状态',
        'detail': '任务详情'
    }

    def pre_add(self, obj):
        interval = obj.interval.split()
        if len(interval) != 5:
            raise ValueError("interval 格式错误，请使用crontab格式")


appbuilder.add_view(TaskModelView, 'Tasks',
                    label='定时任务',
                    icon='fa-indent',
                    category='Tasks Manager',
                    category_label='任务管理',
                    category_icon='fa-tasks')


class TaskRecordModelView(MonitorModelView):
    datamodel = SQLAInterface(TaskRecord)

    base_permissions = ['can_list']
    list_title = '任务记录列表'

    search_columns = ('task_id', 'task_name')
    list_columns = ['task_id', 'task_name', 'result', 'exec_duration', 'created_on', 'changed_on', 'reason']
    order_columns = ['name', 'modified']
    base_order = ('changed_on', 'desc')

    base_filters = [['id', CommonFilter, lambda: []]]
    label_columns = {
        'task_id': '任务ID',
        'task_name': '任务名称',
        'result': '运行结果',
        'reason': '任务详情',
        'duration': '运行时间',
        'created_on': '开始时间',
        'changed_on': '结束时间',
        'exec_duration': '运行时间'
    }


appbuilder.add_view(TaskRecordModelView, 'TaskRecord',
                    label='任务记录',
                    icon='fa-list',
                    category='Tasks Manager',
                    category_label='任务管理',
                    category_icon='fa-tasks')