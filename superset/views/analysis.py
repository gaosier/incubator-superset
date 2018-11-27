# -*- coding:utf-8 -*-
# __author__ = majing
"""
在线分析视图函数
"""
import json

from urllib import parse
from flask import flash, redirect, request, g, Response
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access, has_access_api
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _
from sqlalchemy import or_

from superset import appbuilder, security_manager, db, app
from superset.views.base import SupersetModelView, DeleteMixin, SupersetFilter, FORM_DATA_KEY_BLACKLIST, check_ownership
from superset.utils import validate_json, merge_extra_filters, merge_request_params, json_int_dttm_ser
from superset.connectors.connector_registry import ConnectorRegistry

from superset.models.core import Log, Url
from superset.models.analysis import Analysis, SkModel
from .base import (BaseSupersetView, api, DATASOURCE_MISSING_ERR, get_datasource_access_error_msg, is_owner,
                   json_error_response, json_success, UserInfo)


log_this = Log.log_this
DATASOURCE_ACCESS_ERR = __("You don't have access to this datasource")
config = app.config


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
        'name', 'version', 'sk_model', 'datasource_name', 'owners', 'show_users'
    )
    list_columns = ['name', 'sk_model', 'datasource_link', 'creator', 'modified']
    order_columns = ['name', 'datasource_link', 'modified']
    edit_columns = ['name', 'version', 'description', 'sk_model', 'owners', 'show_users', 'params']
    base_order = ('changed_on', 'desc')
    description_columns = {
        'params': u"分析模型的参数，JSON格式",
        'owners': u"模型的拥有者",
        'show_users': u"模型的共享用户,只有看的权限没有编辑的权限"
    }
    base_filters = [['id', AnalysisFilter, lambda: []]]
    label_columns = {
        'creator': u"创建者",
        'datasource_link': u"表",
        'description': u"描述",
        'modified': u"最后修改时间",
        'owners': u"拥有者",
        'show_users': u"共享用户",
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


class Online(BaseSupersetView):

    @api
    @has_access_api
    @expose('/versions/<name>/')
    def versions(self, name):
        """
        获取分析模型的版本 
        """
        if not name:
            raise ValueError("参数[name]不能为空")

        versions = Analysis.get_versions(name)
        payload = json.dumps(versions)
        return json_success(payload)

    def get_form_data(self, analysis_id=None):
        form_data = {}
        post_data = request.form.get('form_data')
        request_args_data = request.args.get('form_data')
        # Supporting POST
        if post_data:
            form_data.update(json.loads(post_data))
        # request params can overwrite post body
        if request_args_data:
            form_data.update(json.loads(request_args_data))

        url_id = request.args.get('r')
        if url_id:
            saved_url = db.session.query(Url).filter_by(id=url_id).first()
            if saved_url:
                url_str = parse.unquote_plus(
                    saved_url.url.split('?')[1][10:], encoding='utf-8', errors=None)
                url_form_data = json.loads(url_str)
                # allow form_date in request override saved url
                url_form_data.update(form_data)
                form_data = url_form_data

        form_data = {
            k: v
            for k, v in form_data.items()
            if k not in FORM_DATA_KEY_BLACKLIST
        }

        # When a slice_id is present, load from DB and override
        # the form_data from the DB with the other form_data provided
        analysis_id = form_data.get('analysis_id') or analysis_id
        slc = None

        if analysis_id:
            slc = db.session.query(Analysis).filter_by(id=analysis_id).first()
            analysis_form_data = slc.form_data.copy()
            analysis_form_data.update(form_data)
            form_data = analysis_form_data

        return form_data, slc

    @staticmethod
    def datasource_info(datasource_id, datasource_type, form_data):
        """Compatibility layer for handling of datasource info

        datasource_id & datasource_type used to be passed in the URL
        directory, now they should come as part of the form_data,
        This function allows supporting both without duplicating code"""
        datasource = form_data.get('datasource', '')
        if '__' in datasource:
            datasource_id, datasource_type = datasource.split('__')
        datasource_id = int(datasource_id)
        return datasource_id, datasource_type

    def save_slice(self, slc):
        session = db.session()
        msg = 'Analysis [{}] has been saved'.format(slc.name)
        session.add(slc)
        session.commit()
        flash(msg, 'info')

    def overwrite_slice(self, slc):
        session = db.session()
        session.merge(slc)
        session.commit()
        msg = 'Analysis [{}] has been overwritten'.format(slc.name)
        flash(msg, 'info')


    def save_or_overwrite(
            self, args, slc, slice_add_perm, slice_overwrite_perm, datasource_id, datasource_type, datasource_name):
        """Save or overwrite a analysis"""
        analysis_name = args.get('analysis_name')
        action = args.get('action')
        form_data, _ = self.get_form_data()

        if action in ('saveas'):
            if 'analysis_id' in form_data:
                form_data.pop('analysis_id')
            slc = Analysis(owners=[g.user] if g.user else [])

        slc.params = json.dumps(form_data)
        slc.datasource_name = datasource_name
        slc.datasource_type = datasource_type
        slc.datasource_id = datasource_id
        slc.name = analysis_name

        if action in ('saveas') and slice_add_perm:
            self.save_slice(slc)
        elif action == 'overwrite' and slice_overwrite_perm:
            self.overwrite_slice(slc)

        response = {
            'can_add': slice_add_perm,
            'can_overwrite': is_owner(slc, g.user),
            'form_data': slc.form_data,
            'slice': slc.data,
        }

        return json_success(json.dumps(response))

    @log_this
    @has_access
    @expose('/analysis/<datasource_type>/<datasource_id>/', methods=['GET', 'POST'])
    @expose('/analysis/', methods=['GET', 'POST'])
    def analysis(self, datasource_type=None, datasource_id=None):
        user_id = g.user.get_id() if g.user else None
        form_data, slc = self.get_form_data()
        datasource_id, datasource_type = self.datasource_info(
            datasource_id, datasource_type, form_data)

        error_redirect = '/analysismodelview/list/'
        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            flash(DATASOURCE_MISSING_ERR, 'danger')
            return redirect(error_redirect)

        if not security_manager.datasource_access(datasource):
            flash(
                __(get_datasource_access_error_msg(datasource.name)),
                'danger')
            return redirect(
                'superset/request_access/?'
                'datasource_type={datasource_type}&'
                'datasource_id={datasource_id}&'
                ''.format(**locals()))

        # slc perms
        slice_add_perm = security_manager.can_access('can_add', 'AnalysisModelView')
        slice_overwrite_perm = is_owner(slc, g.user)

        form_data['datasource'] = str(datasource_id) + '__' + datasource_type

        # On explore, merge extra filters into the form data
        merge_extra_filters(form_data)

        # merge request url params
        if request.method == 'GET':
            merge_request_params(form_data, request.args)

        # handle save or overwrite
        action = request.args.get('action')

        if action == 'overwrite' and not slice_overwrite_perm:
            return json_error_response(
                _('You don\'t have the rights to ') + _('alter this ') + _('chart'),
                status=400)

        if action == 'saveas' and not slice_add_perm:
            return json_error_response(
                _('You don\'t have the rights to ') + _('create a ') + _('analysis'),
                status=400)

        if action in ('saveas', 'overwrite'):
            return self.save_or_overwrite(
                request.args,
                slc, slice_add_perm,
                slice_overwrite_perm,
                datasource_id,
                datasource_type,
                datasource.name)
        if slc:
            datasource.slice_users = [slc.created_by_fk, ]

        standalone = request.args.get('standalone') == 'true'
        bootstrap_data = {
            'can_add': slice_add_perm,
            'can_overwrite': slice_overwrite_perm,
            'datasource': datasource.data,
            'form_data': form_data,
            'datasource_id': datasource_id,
            'datasource_type': datasource_type,
            'slice': slc.data if slc else None,
            'standalone': standalone,
            'user_id': user_id,
            'forced_height': request.args.get('height'),
            'common': self.common_bootsrap_payload(),
        }
        table_name = datasource.table_name \
            if datasource_type == 'table' \
            else datasource.datasource_name
        title = slc.slice_name if slc else 'Analysis - ' + table_name
        return self.render_template(
            'superset/basic.html',
            bootstrap_data=json.dumps(bootstrap_data),
            entry='analysis',
            title=title,
            standalone_mode=standalone)

    @api
    @has_access_api
    @expose('/columns/<datasource_type>/<datasource_id>/')
    def columns(self, datasource_type, datasource_id):
        data = []
        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            return json_error_response(DATASOURCE_MISSING_ERR)
        if not security_manager.datasource_access(datasource):
            return json_error_response(DATASOURCE_ACCESS_ERR)

        columns = datasource.columns
        for item in columns:
            if item.filterable:
                if item.owners:
                    if g.user in item.owners:
                        data.append({"name": item.column_name, "verbose_name": item.verbose_name})
                else:
                    data.append({"name": item.column_name, "verbose_name": item.verbose_name})
        payload = json.dumps(data)
        return json_success(payload)

    @api
    @has_access_api
    @expose('/filter/<datasource_type>/<datasource_id>/<column>/')
    def filter(self, datasource_type, datasource_id, column):
        """
        Endpoint to retrieve values for specified column.

        :param datasource_type: Type of datasource e.g. table
        :param datasource_id: Datasource id
        :param column: Column name to retrieve values for
        :return:
        """
        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            return json_error_response(DATASOURCE_MISSING_ERR)
        if not security_manager.datasource_access(datasource):
            return json_error_response(DATASOURCE_ACCESS_ERR)

        payload = json.dumps(
            datasource.values_for_column(
                column,
                config.get('FILTER_SELECT_ROW_LIMIT', 10000),
            ),
            default=json_int_dttm_ser)
        return json_success(payload)


    @api
    @has_access_api
    @expose('/skmodels/')
    def names(self):
        data = SkModel.names()
        payload = json.dumps(data)
        return json_success(payload)

    @api
    @has_access_api
    @expose('/datasources/')
    def datasources(self):
        datasources = ConnectorRegistry.get_all_datasources(db.session)
        datasources = [o.name for o in datasources]

        if UserInfo.has_all_datasource_access():
            data = datasources
        else:
            perms = UserInfo.get_view_menus('datasource_access')
            data = [item for item in datasources if item.get("perm") in perms]

        datasources = sorted(data, key=lambda x: x)
        datasources = json.dumps(datasources)
        return json_success(datasources)

appbuilder.add_view_no_menu(Online)






