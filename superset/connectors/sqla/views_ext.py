#-*-coding:utf-8-*-
from flask_appbuilder.views import GeneralView,ModelView,MasterDetailView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import gettext as __

from superset import appbuilder
from . import models,models_ext
from .views import TableModelView,TableColumnInlineView,SqlMetricInlineView
from superset.views.core_ext import TableColumnFilter
from superset.views.core import check_ownership

class MyTableColumnInlineView(TableColumnInlineView):
    edit_columns = [
        'column_name', 'verbose_name', 'description',
        'type', 'groupby', 'filterable','count_distinct', 'sum', 'avg', 'min', 'max',
        'table',  'expression',
        'is_dttm']
    add_columns = edit_columns
    base_filters = [['id', TableColumnFilter, lambda: []]]
    list_columns = [
        'column_name', 'verbose_name', 'type', 'groupby', 'filterable', 'is_dttm','count_distinct', 'sum', 'avg', 'min', 'max','created_by' ]
    def pre_update(self, obj):
        check_ownership(obj)

    def pre_delete(self, obj):
        check_ownership(obj)

appbuilder.add_view_no_menu(MyTableColumnInlineView)

class MySqlMetricInlineView(SqlMetricInlineView):
    list_columns = ['metric_name', 'verbose_name', 'metric_type','created_by']
    edit_columns = [
        'metric_name', 'description', 'verbose_name', 'metric_type',
        'expression', 'table',]
    add_columns = edit_columns
    base_filters = [['id', TableColumnFilter, lambda: []]]
    def pre_update(self, obj):
        check_ownership(obj)

    def pre_delete(self, obj):
        check_ownership(obj)
appbuilder.add_view_no_menu(MySqlMetricInlineView)

class MyTableModelView(TableModelView):
    edit_columns=['table_name']
    related_views = [MyTableColumnInlineView,MySqlMetricInlineView]
    def pre_update(self, obj):
        check_ownership(obj)

appbuilder.add_view_no_menu(MyTableModelView)
# appbuilder.add_view(
#     MyTableModelView,
#     "My Tables",
#     label="自定义数据集",
#     icon="fa-table",
#     category="",
#     category_icon='',)


class TableGroupView(MasterDetailView):
    list_title = '数据集分类'
    datamodel = SQLAInterface(models_ext.SqlTableGroup)
    related_views = [MyTableModelView]


appbuilder.add_view(
    TableGroupView,
    'TableGroups',
    #label=__('TableGroups'),
    label='自定义数据集',
    category='',
    icon='fa-table',
    href='/tablegroupview/list/1',
)
appbuilder.add_separator("Sources")

