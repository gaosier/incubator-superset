# -*-coding:utf-8-*-
import json
from flask import request
from flask_appbuilder.views import MasterDetailView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.urltools import get_page_args, get_page_size_args, get_order_args

from superset import appbuilder, db
from . models import SqlTableGroup, SqlaTable
from .views import TableModelView,TableColumnInlineView,SqlMetricInlineView
from superset.views.base_ext import PermManager, login_required
from superset.views.core_ext import TableColumnFilter
from superset.views.core import check_ownership, json_success, json_error_response
from superset.views.base import api

from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access
from flask_appbuilder.security.views import AuthDBView
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
    datamodel = SQLAInterface(SqlTableGroup)
    related_views = [MyTableModelView]
    base_order = ('sort_id', 'asc')
    login_view = AuthDBView

    list_columns = ['name']
    list_template = 'superset/datacenter/datacenter.html'
    page_size = 20

    def get_table_groups(self, permission, parent_id):
        if permission.has_all_datasource_access():
            data = SqlTableGroup.get_group_menus(parent_id)
        else:
            views = list(permission.get_view_menus("datasource_access"))
            group_ids = SqlaTable.get_group_ids(views, parent_id)
            data = SqlTableGroup.get_groups_by_ids(group_ids)
        return data


    @api
    @expose('/menu/<int:parent_id>/')
    @login_required
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

    @api
    @expose('/tables/<pk>/')
    @login_required
    def tables(self, pk=None):
        if pk is None:
            return json_error_response(u"参数pk为空")

        permission = PermManager()
        if permission.has_all_datasource_access():
            perms = None
        else:
            perms = permission.get_view_menus('datasource_access')

        data = SqlaTable.get_table_list(pk, perms)
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
    @api
    @expose('/search/table/')
    @login_required
    def search_table(self):
        """
        搜索表 表的中文名/英文名
        :return: 返回当前用户有权限的表
        """
        permission = PermManager()
        if permission.has_all_datasource_access():
            tables = self.get_all_tables()
        else:
            perms = permission.get_view_menus('datasource_access')
            tables = self.get_tables_by_perms(perms)

        data = self.get_group_names(tables)
        return json_success(json.dumps(data))

    def get_all_tables(self):
        querys = db.session.query(SqlaTable.id, SqlaTable.table_name, SqlaTable.verbose_name, SqlTableGroup.parent_id,
                                  SqlaTable.group_id).outerjoin(SqlTableGroup).filter(SqlaTable.group_id != None).all()
        return querys

    def get_tables_by_perms(self, perms):
        if not perms:
            return []

        querys = db.session.query(SqlaTable.id, SqlaTable.table_name, SqlaTable.verbose_name, SqlTableGroup.parent_id,
                                  SqlaTable.group_id).outerjoin(SqlTableGroup).filter(SqlaTable.group_id != None,
                                                                                        SqlaTable.perm.in_(perms)).all()

        return querys

    def get_group_names(self, tabs):
        """
        获取table所在的分类的名字  一级菜单和二级菜单
        :param tabs: 
        :return: 
        """
        groups_name = SqlTableGroup.all_group_names() or {}

        data = []
        for tab in tabs:
            tab = list(tab)
            if tab[3] == 0:
                group_id = tab[4]
                tab[3] = groups_name.get(group_id, '')
                tab[4] = ''
            else:
                tab[3] = groups_name.get(tab[3], '')
                tab[4] = groups_name.get(tab[4], '')
            data.append(tab)
        return data


appbuilder.add_view(
    TableGroupView,
    'TableGroups',
    label='数据中心',
    category='',
    icon='fa-table',
    href='/tablegroupview/list/1/',
)

