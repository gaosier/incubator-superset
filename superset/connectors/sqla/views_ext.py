#-*-coding:utf-8-*-
from flask_appbuilder.views import GeneralView,ModelView,MasterDetailView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import gettext as __

from superset import appbuilder
from . import models,models_ext
from .views import TableModelView


class TableGroupView(MasterDetailView):
    list_title = '数据集分类'
    datamodel = SQLAInterface(models_ext.SqlTableGroup)
    related_views = [TableModelView]


appbuilder.add_view(
    TableGroupView,
    'TableGroups',
    #label=__('TableGroups'),
    label='数据集分类',
    category='Sources',
    category_label=__('Sources'),
    icon='fa-table',
    href='/tablegroupview/list/1',
)
appbuilder.add_separator("Sources")

