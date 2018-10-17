# -*-coding:utf-8-*-
import json
from flask import request
from flask_appbuilder.views import GeneralView,ModelView,MasterDetailView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import gettext as __

from superset import appbuilder
from . import models_ext, models
from .views import TableModelView,TableColumnInlineView,SqlMetricInlineView
from superset.views.core_ext import TableColumnFilter
from superset.views.core import check_ownership, json_success, json_error_response

from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access
from past.builtins import basestring


class MyTableColumnInlineView(TableColumnInlineView):
    edit_columns = [
        'column_name', 'verbose_name', 'description',
        'type', 'groupby', 'filterable','count_distinct', 'sum', 'avg', 'min', 'max',
        'expression', 'is_dttm']
    add_columns = edit_columns
    base_filters = [['id', TableColumnFilter, lambda: []]]
    list_columns = [
        'column_name', 'verbose_name', 'type', 'groupby', 'filterable', 'is_dttm','count_distinct', 'sum', 'avg', 'min', 'max','created_by' ]

    def pre_update(self, obj):
        check_ownership(obj)

    def pre_delete(self, obj):
        check_ownership(obj)

    def pre_add(self, obj):
        table_id = request.full_path.split('=')[1] if len(request.full_path.split('=')) == 2 else None
        obj.table_id = int(table_id)

appbuilder.add_view_no_menu(MyTableColumnInlineView)


class MySqlMetricInlineView(SqlMetricInlineView):
    list_columns = ['metric_name', 'verbose_name', 'metric_type','created_by']
    edit_columns = [
        'metric_name', 'description', 'verbose_name', 'metric_type',
        'expression']
    add_columns = edit_columns
    base_filters = [['id', TableColumnFilter, lambda: []]]

    def pre_update(self, obj):
        check_ownership(obj)

    def pre_delete(self, obj):
        check_ownership(obj)

    def pre_add(self, obj):
        table_id = request.full_path.split('=')[1] if len(request.full_path.split('=')) == 2 else None
        obj.table_id = int(table_id)


appbuilder.add_view_no_menu(MySqlMetricInlineView)


class MyTableModelView(TableModelView):
    edit_columns=['table_name']
    related_views = [MyTableColumnInlineView,MySqlMetricInlineView]

    def pre_update(self, obj):
        check_ownership(obj)

    @expose('/edit/<pk>', methods=['GET', 'POST'])
    @has_access
    def edit(self, pk):
        """Simple hack to redirect to explore view after saving"""
        resp = super(TableModelView, self).edit(pk)
        if isinstance(resp, basestring):
            return resp
        return resp


appbuilder.add_view_no_menu(MyTableModelView)


class TableGroupView(MasterDetailView):
    list_title = '数据集分类'
    datamodel = SQLAInterface(models_ext.SqlTableGroup)
    related_views = [MyTableModelView]
    base_order = ('sort_id', 'asc')

    list_columns = ['name']
    page_size = 20

    @expose('/menu/<int:parent_id>/')
    def menus(self, parent_id):
        """
        获取数据集分类
        """
        if parent_id is None:
            return json_error_response(u"参数paren_id为空")
        data = models_ext.SqlTableGroup.get_group_menus(parent_id)
        return json_success(json.dumps({"data": data}))

    @expose('/list/')
    @expose('/list/<pk>')
    @has_access
    def list(self, pk=None):
        if pk is None:
            return json_error_response(u"参数pk为空")
        data = models.SqlaTable.get_table_list(pk)
        return json_success(json.dumps(data))




appbuilder.add_view(
    TableGroupView,
    'TableGroups',
    label='数据中心',
    category='',
    icon='fa-table',
    href='/tablegroupview/list/1',
)

