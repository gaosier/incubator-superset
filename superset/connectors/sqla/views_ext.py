# -*-coding:utf-8-*-
import json
from flask import request
from flask_appbuilder.views import MasterDetailView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.urltools import get_page_args, get_page_size_args, get_order_args

from superset import appbuilder
from . import models_ext, models
from .views import TableModelView,TableColumnInlineView,SqlMetricInlineView
from superset.views.base_ext import PermManager
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
    list_template = 'superset/datacenter/datacenter.html'
    page_size = 20

    def get_table_groups(self, permission, parent_id):
        if permission.has_all_datasource_access():
            data = models_ext.SqlTableGroup.get_group_menus(parent_id)
        else:
            views = list(permission.get_view_menus("datasource_access"))
            group_ids = models.SqlaTable.get_group_ids(views, parent_id)
            data = models_ext.SqlTableGroup.get_groups_by_ids(group_ids)
        return data


    @has_access
    @expose('/menu/<int:parent_id>/')
    def menu(self, parent_id):
        """
        获取数据集分类
        """
        if parent_id is None:
            return json_error_response(u"参数paren_id为空")

        permission = PermManager()
        if not permission.has_perm('can_list', 'TableGroupView'):
            return json_error_response('you do not have permission to access the menu')

        data = self.get_table_groups(permission, parent_id)
        return json_success(json.dumps({"data": data}))

    @has_access
    @expose('/tables/<pk>/')
    def tables(self, pk=None):
        if pk is None:
            return json_error_response(u"参数pk为空")

        permission = PermManager()
        if permission.has_all_datasource_access():
            perms = None
        else:
            perms = permission.get_view_menus('datasource_access')

        data = models.SqlaTable.get_table_list(pk, perms)
        return json_success(json.dumps(data))

    @expose('/list/')
    @expose('/list/<pk>/')
    @has_access
    def list(self, pk=None):
        pages = get_page_args()
        page_sizes = get_page_size_args()
        orders = get_order_args()

        widgets = self._list()
        if pk:
            item = self.datamodel.get(pk)
            widgets = self._get_related_views_widgets(item, orders=orders,
                                                      pages=pages, page_sizes=page_sizes, widgets=widgets)
            related_views = self._related_views
        else:
            related_views = []

        return self.render_template(self.list_template,
                                    title=self.list_title,
                                    widgets=widgets,
                                    entry='datacenter',
                                    related_views=related_views,
                                    master_div_width=self.master_div_width)


appbuilder.add_view(
    TableGroupView,
    'TableGroups',
    label='数据中心',
    category='',
    icon='fa-table',
    href='/tablegroupview/list/1/',
)

