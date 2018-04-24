"""Views used by the SqlAlchemy connector"""
import logging

from past.builtins import basestring

from flask import Markup, flash, redirect
from flask_appbuilder import CompactCRUDMixin, expose
from superset.fab.models.sqla.interface import SupersetSQLAInterface as SQLAInterface
import sqlalchemy as sa

from flask_babel import lazy_gettext as _
from flask_babel import gettext as __

from superset import appbuilder, db, utils, security, sm
from superset.utils import has_access
from superset.connectors.base.views import DatasourceModelView
from superset.views.base import (
    SupersetModelView, ListWidgetWithCheckboxes, DeleteMixin, DatasourceFilter,TableColumnFilter,
    get_datasource_exist_error_mgs,
)
from superset.utils import metric_format
from . import models
from superset.views.core import check_ownership
from flask_appbuilder.views import GeneralView,ModelView,MasterDetailView

class TableColumnInlineView(CompactCRUDMixin, SupersetModelView):  # noqa
    datamodel = SQLAInterface(models.TableColumn)

    list_title = _('List Columns')
    show_title = _('Show Column')
    add_title = _('Add Column')
    edit_title = _('Edit Column')

    can_delete = False
    list_widget = ListWidgetWithCheckboxes
    edit_columns = [
        'column_name', 'verbose_name', 'description',
        'type', 'groupby', 'filterable',
        'table', 'count_distinct', 'sum','avg', 'min', 'max', 'expression',
        'is_dttm', 'python_date_format', 'database_expression', 'partition_expression','order_number']
    add_columns = edit_columns
    list_columns = [
        'order_number','column_name', 'verbose_name', 'type', 'groupby', 'filterable', 'count_distinct',
        'sum','avg', 'min', 'max', 'is_dttm', 'is_partition','is_memcached','is_active']
    page_size = 80
    description_columns = {
        'is_dttm': _(
            "Whether to make this column available as a "
            "[Time Granularity] option, column has to be DATETIME or "
            "DATETIME-like"),
        'filterable': _(
            "Whether this column is exposed in the `Filters` section "
            "of the explore view."),
        'type': _(
            "The data type that was inferred by the database. "
            "It may be necessary to input a type manually for "
            "expression-defined columns in some cases. In most case "
            "users should not need to alter this."),
        'expression': utils.markdown(
            "a valid SQL expression as supported by the underlying backend. "
            "Example: `substr(name, 1, 1)`", True),
        'python_date_format': utils.markdown(Markup(
            "The pattern of timestamp format, use "
            "<a href='https://docs.python.org/2/library/"
            "datetime.html#strftime-strptime-behavior'>"
            "python datetime string pattern</a> "
            "expression. If time is stored in epoch "
            "format, put `epoch_s` or `epoch_ms`. Leave `Database Expression` "
            "below empty if timestamp is stored in "
            "String or Integer(epoch) type"), True),
        'database_expression': utils.markdown(
            "The database expression to cast internal datetime "
            "constants to database date/timestamp type according to the DBAPI. "
            "The expression should follow the pattern of "
            "%Y-%m-%d %H:%M:%S, based on different DBAPI. "
            "The string should be a python string formatter \n"
            "`Ex: TO_DATE('{}', 'YYYY-MM-DD HH24:MI:SS')` for Oracle"
            "Superset uses default expression based on DB URI if this "
            "field is blank.", True),
    }
    label_columns = {
        'column_name': _("Column"),
        'verbose_name': _("Verbose Name"),
        'description': _("Description"),
        'groupby': _("Groupable"),
        'filterable': _("Filterable"),
        'table': _("Table"),
        'count_distinct': _("Count Distinct"),
        'sum': _("Sum"),
        'avg':_("Avg"),
        'min': _("Min"),
        'max': _("Max"),
        'expression': _("Expression"),
        'is_dttm': _("Is temporal"),
        'python_date_format': _("Datetime Format"),
        'database_expression': _("Database Expression"),
        'type': _('Type'),
        'is_partition': _("Is Partition"),
        'is_memcached': _("Is Memcached"),
        'partition_expression': _("Partition Expression"),
    }
    def post_delete(self, item):
        """
            #删除时，同时删除metric表内的相关信息
        """
        dic=self.metric_name_dic(item)
        Metric_dict = db.session.query(models.SqlMetric).filter(models.SqlMetric.table_id == item.table_id,
                                                                models.SqlMetric.metric_name.in_(list(dic))).all()
        for m in Metric_dict:
            db.session.delete(m)
        db.session.commit()

    def post_add(self, item):
        dic=self.metric_name_dic(item)
        for n in dic:
            if dic[n]['flag']:
                args = metric_format(dic[n]['value'], item)
                db.session.add(models.SqlMetric(**args))
                db.session.commit()

    def metric_name_dic(self,item):
        return {'sum__' + item.column_name: {'flag': item.sum, 'value': 'sum'},
               'avg__' + item.column_name: {'flag': item.avg, 'value': 'avg'},
               'max__' + item.column_name: {'flag': item.max, 'value': 'max'},
               'min__' + item.column_name: {'flag': item.min, 'value': 'min'},
               'count_distinct__' + item.column_name: {'flag': item.count_distinct, 'value': 'count_distinct'}}

    def post_update(self, item):
        """
            #编辑后 影响metric表的数据
        """
        dic = self.metric_name_dic(item)
        Metric_dict = db.session.query(models.SqlMetric).filter(models.SqlMetric.table_id == item.table_id,
                                                                models.SqlMetric.metric_name.in_(list(dic))).all()
        metric_in = set({})
        for m in Metric_dict:
            metric_in.add(m.metric_name)
            if not dic[m.metric_name]['flag']:
                db.session.delete(m)
                db.session.commit()
        for n in list(set(dic) - metric_in):
            if dic[n]['flag']:
                args = metric_format(dic[n]['value'], item)
                db.session.add(models.SqlMetric(**args))
                db.session.commit()
appbuilder.add_view_no_menu(TableColumnInlineView)


class SqlMetricInlineView(CompactCRUDMixin, SupersetModelView):  # noqa
    datamodel = SQLAInterface(models.SqlMetric)

    list_title = _('List Metrics')
    show_title = _('Show Metric')
    add_title = _('Add Metric')
    edit_title = _('Edit Metric')

    list_columns = ['metric_name', 'verbose_name', 'metric_type']
    edit_columns = [
        'metric_name', 'description', 'verbose_name', 'metric_type',
        'expression', 'table', 'd3format', 'is_restricted']
    description_columns = {
        'expression': utils.markdown(
            "a valid SQL expression as supported by the underlying backend. "
            "Example: `count(DISTINCT userid)`", True),
        'is_restricted': _("Whether the access to this metric is restricted "
                           "to certain roles. Only roles with the permission "
                           "'metric access on XXX (the name of this metric)' "
                           "are allowed to access this metric"),
        'd3format': utils.markdown(
            "d3 formatting string as defined [here]"
            "(https://github.com/d3/d3-format/blob/master/README.md#format). "
            "For instance, this default formatting applies in the Table "
            "visualization and allow for different metric to use different "
            "formats", True
        ),
    }
    add_columns = edit_columns
    page_size = 80
    label_columns = {
        'metric_name': _("Metric"),
        'description': _("Description"),
        'verbose_name': _("Verbose Name"),
        'metric_type': _("Type"),
        'expression': _("SQL Expression"),
        'table': _("Table"),
        'd3format': _("D3 Format"),
        'is_restricted': _('Is Restricted')
    }

    def post_add(self, metric):
        if metric.is_restricted:
            security.merge_perm(sm, 'metric_access', metric.get_perm())

    def post_update(self, metric):
        if metric.is_restricted:
            security.merge_perm(sm, 'metric_access', metric.get_perm())

appbuilder.add_view_no_menu(SqlMetricInlineView)


class TableModelView(DatasourceModelView, DeleteMixin):  # noqa
    datamodel = SQLAInterface(models.SqlaTable)
        
    list_title = _('List Tables')
    show_title = _('Show Table')
    add_title = _('Add Table')
    edit_title = _('Edit Table')

    list_columns = [
        'link', 'database',
        'changed_by_', 'modified']
    order_columns = ['modified']
    add_columns = ['database', 'table_name','verbose_name']
    edit_columns = [
        'table_name', 'sql', 'filter_select_enabled', 'slices',
        'fetch_values_predicate', 'database', 'schema','verbose_name', 
        'description', 'owner',
        'main_dttm_col', 'default_endpoint', 'offset', 'cache_timeout']
    show_columns = edit_columns + ['perm']
    related_views = [TableColumnInlineView, SqlMetricInlineView]
    base_order = ('verbose_name', 'desc')
    search_columns = (
        # 'database', 'schema', 'table_name', 'owner',
        'database', 'schema', 'verbose_name', 'owner',
    )
    description_columns = {
        'slices': _(
            "The list of slices associated with this table. By "
            "altering this datasource, you may change how these associated "
            "slices behave. "
            "Also note that slices need to point to a datasource, so "
            "this form will fail at saving if removing slices from a "
            "datasource. If you want to change the datasource for a slice, "
            "overwrite the slice from the 'explore view'"),
        'offset': _("Timezone offset (in hours) for this datasource"),
        'table_name': _(
            "Name of the table that exists in the source database"),
        'schema': _(
            "Schema, as used only in some databases like Postgres, Redshift "
            "and DB2"),
        'description': Markup(
            "Supports <a href='https://daringfireball.net/projects/markdown/'>"
            "markdown</a>"),
        'sql': _(
            "This fields acts a Superset view, meaning that Superset will "
            "run a query against this string as a subquery."
        ),
        'fetch_values_predicate': _(
            "Predicate applied when fetching distinct value to "
            "populate the filter control component. Supports "
            "jinja template syntax. Applies only when "
            "`Enable Filter Select` is on."
        ),
        'default_endpoint': _(
            "Redirects to this endpoint when clicking on the table "
            "from the table list"),
        'filter_select_enabled': _(
            "Whether to populate the filter's dropdown in the explore "
            "view's filter section with a list of distinct values fetched "
            "from the backend on the fly"),
    }
    base_filters = [['id', DatasourceFilter, lambda: []]]
    label_columns = {
        'slices': _("Associated Slices"),
        'link': _("Table"),
        'changed_by_': _("Changed By"),
        'database': _("Database"),
        'changed_on_': _("Last Changed"),
        'filter_select_enabled': _("Enable Filter Select"),
        'schema': _("Schema"),
        'default_endpoint': _('Default Endpoint'),
        'offset': _("Offset"),
        'cache_timeout': _("Cache Timeout"),
        'table_name': _("Table Name"),
        'fetch_values_predicate': _('Fetch Values Predicate'),
        'owner': _("Owner"),
        'main_dttm_col': _("Main Datetime Column"),
        'description': _('Description'),
        'verbose_name':_('Verbose Name'),
    }

    def pre_add(self, table):
        # print(table,type(table),sa.func.count('*'),909090909009090,models.SqlaTable.table_name,
        #       type(models.SqlaTable))
        number_of_existing_tables = db.session.query(
            sa.func.count('*')).filter(
            models.SqlaTable.table_name == table.table_name,
            models.SqlaTable.schema == table.schema,
            models.SqlaTable.database_id == table.database.id
        ).scalar()
        # table object is already added to the session
        if number_of_existing_tables > 1:
            raise Exception(get_datasource_exist_error_mgs(table.full_name))

        # Fail before adding if the table can't be found
        try:
            table.get_sqla_table_object()
        except Exception as e:
            logging.exception(e)
            raise Exception(_(
                "Table [{}] could not be found, "
                "please double check your "
                "database connection, schema, and "
                "table name").format(table.name))

    def post_add(self, table, flash_message=True):
        table.fetch_metadata()
        security.merge_perm(sm, 'datasource_access', table.get_perm())
        if table.schema:
            security.merge_perm(sm, 'schema_access', table.schema_perm)

        if flash_message:
            flash(_(
                "The table was created. "
                "As part of this two phase configuration "
                "process, you should now click the edit button by "
                "the new table to configure it."), "info")

    def post_update(self, table):
        self.post_add(table, flash_message=False)

    def _delete(self, pk):
        DeleteMixin._delete(self, pk)


appbuilder.add_view(
    TableModelView,
    "Tables",
    label=__("Tables"),
    category="Sources",
    category_label=__("Sources"),
    icon='fa-table',)

appbuilder.add_separator("Sources")

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
    list_title = '数据中心分类'
    datamodel = SQLAInterface(models.SqlTableGroup)
    related_views = [MyTableModelView]


appbuilder.add_view(
    TableGroupView,
    'TableGroups',
    #label=__('TableGroups'),
    label='数据中心',
    category='',
    icon='fa-table',
    href='/tablegroupview/list/1',
)