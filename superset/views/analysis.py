# -*- coding:utf-8 -*-
# __author__ = majing
"""
在线分析视图函数
"""
import json

from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access
from sqlalchemy import or_

from superset import appbuilder, security_manager, db
from superset.views.base import SupersetModelView, DeleteMixin, SupersetFilter
from superset.utils import validate_json
from superset.views.core import check_ownership
from superset.connectors.connector_registry import ConnectorRegistry

from superset.models.analysis import Analysis, SkModel
from .base import BaseSupersetView


class SkModelView(SupersetModelView, DeleteMixin):
    datamodel = SQLAInterface(SkModel)

    list_title = u"机器学习模型"
    show_title = u"结果展示"
    add_title = u"添加模型"
    edit_title = u"编辑模型"

    search_columns = ('name', 'full_name')
    list_columns = ['name', 'full_name', 'creator', 'modified']
    order_columns = ['name', 'modified']
    edit_columns = ['name', 'full_name', 'params']
    add_columns = edit_columns
    base_order = ('changed_on', 'desc')
    description_columns = {
        'params': u"机器学习模型的参数，JSON格式",
    }

    label_columns = {
        'creator': u"创建者",
        'full_name': u"全称",
        'description': u"描述",
        'modified': u"最后修改时间",
        'params': u"参数",
        'name': u"名称",
    }

    def pre_add(self, obj):
        validate_json(obj.params)

    def pre_update(self, obj):
        validate_json(obj.params)


appbuilder.add_view(SkModelView, 'SkModelView', icon="fa-book", label=u"机器学习模型", category_icon="fa-table",
                    category=u"Online Analysis", category_label=u"在线分析")


class AnalysisFilter(SupersetFilter):
    def apply(self, query, value):
        if self.has_all_datasource_access():
            return query
        perms = self.get_view_menus('datasource_access')
        User = security_manager.user_model
        owner_ids_qry = (
            db.session
                .query(Analysis.id)
                .join(Analysis.owners)
                .filter(User.id == User.get_user_id())
        )

        show_user_ids_qry = (
            db.session
                .query(Analysis.id)
                .join(Analysis.show_users)
                .filter(User.id == User.get_user_id())
        )

        return query.filter(Analysis.perm.in_(perms)).filter(or_(Analysis.id.in_(owner_ids_qry),
                                                                 Analysis.id.in_(show_user_ids_qry)))


class AnalysisModelView(SupersetModelView, DeleteMixin):
    datamodel = SQLAInterface(Analysis)

    list_title = u"分析模型列表"
    show_title = u"结果展示"
    add_title = u"添加模型"
    edit_title = u"编辑模型"

    search_columns = (
        'name', 'version', 'sk_model', 'datasource_name', 'owner', 'show_user'
    )
    list_columns = ['name', 'sk_model', 'datasource_link', 'creator', 'modified']
    order_columns = ['name', 'datasource_link', 'modified']
    edit_columns = ['name', 'version', 'description', 'sk_model', 'owner', 'show_user', 'params']
    base_order = ('changed_on', 'desc')
    description_columns = {
        'params': u"分析模型的参数，JSON格式",
        'owner': u"模型的拥有者",
        'show_user': u"模型的共享用户,只有看的权限没有编辑的权限"
    }
    base_filters = [['id', AnalysisFilter, lambda: []]]
    label_columns = {
        'creator': u"创建者",
        'datasource_link': u"表",
        'description': u"描述",
        'modified': u"最后修改时间",
        'owner': u"拥有者",
        'show_user': u"共享用户",
        'params': u"参数",
        'name': u"名称",
        'sk_model': u"机器学习模型",
        'version': u"版本"
    }

    def pre_add(self, obj):
        validate_json(obj.params)

    def pre_update(self, obj):
        validate_json(obj.params)
        check_ownership(obj)

    def pre_delete(self, obj):
        check_ownership(obj)

    @expose('/add', methods=['GET', 'POST'])
    @has_access
    def add(self):
        datasources = ConnectorRegistry.get_all_datasources(db.session)
        datasources = [
            {'value': str(d.id) + '__' + d.type, 'label': repr(d)}
            for d in datasources
        ]
        return self.render_template(
            'superset/add_analysis.html',
            bootstrap_data=json.dumps({
                'datasources': sorted(datasources, key=lambda d: d['label']),
            }),
        )

appbuilder.add_view(AnalysisModelView, 'Analysis', icon="fa-comments", label=u"分析模型", category_icon="analytics", category=u"Online Analysis",
                    category_label=u"在线分析")


class OnlineAnalysis(BaseSupersetView):
    def versions(self):
        """
        获取分析模型的版本 
        """
        pass



