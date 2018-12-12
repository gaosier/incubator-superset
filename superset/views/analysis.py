# -*- coding:utf-8 -*-
# __author__ = majing
"""
在线分析视图函数
"""
import json
import os
import uuid
import time
import logging

from urllib import parse
from flask import flash, redirect, request, g, render_template, send_file, send_from_directory, make_response
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder import expose
from flask_appbuilder.security.decorators import has_access, has_access_api
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _
from sqlalchemy import or_
from werkzeug.utils import secure_filename
from pygments import highlight, lexers
from pygments.formatters import HtmlFormatter

from superset import appbuilder, security_manager, db, app
from superset.views.base import SupersetModelView, DeleteMixin, SupersetFilter, FORM_DATA_KEY_BLACKLIST, check_ownership
from superset.utils import validate_json, merge_extra_filters, merge_request_params, json_int_dttm_ser
from superset.connectors.connector_registry import ConnectorRegistry
from superset.sk_model import sk_types

from superset.models.core import Log, Url
from superset.models.analysis import Analysis, SkModel
from .base import (BaseSupersetView, api, DATASOURCE_MISSING_ERR, get_datasource_access_error_msg, is_owner,
                   json_error_response, json_success, UserInfo, REQ_PARAM_NULL_ERR)


log_this = Log.log_this
DATASOURCE_ACCESS_ERR = __("You don't have access to this datasource")
config = app.config

CURRENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SK_MODEL_PATH = os.path.join(CURRENT_DIR, "sk_model.py")


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
        'name','version', 'sk_model', 'datasource_name', 'owners', 'show_users'
    )
    list_columns = ['name_link', 'sk_model', 'datasource_link', 'creator', 'modified']
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
        'name_link': u"名称",
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
    def datasource_info(form_data, datasource_id=None, datasource_type=None):
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

    def save_or_overwrite(self, args, slc, slice_add_perm, slice_overwrite_perm, datasource_id, datasource_type,
                          datasource_name):
        """
        保存或者覆盖
        """
        analysis_name = args.get('name')
        action = args.get('action')
        version = args.get('version')
        form_data, _ = self.get_form_data()
        sk = SkModel.get_instance(form_data.get("sk_type"))

        if action in ('saveas'):
            if 'analysis_id' in form_data:
                form_data.pop('analysis_id')

            slc = Analysis(owners=[g.user] if g.user else [])

        slc.params = json.dumps(form_data)
        slc.datasource_name = datasource_name
        slc.datasource_type = datasource_type
        slc.datasource_id = datasource_id
        slc.name = analysis_name
        slc.sk_model = sk
        slc.version = version

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
        datasource_id, datasource_type = self.datasource_info(form_data,
            datasource_id, datasource_type)

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
            'form_data': form_data,
            'datasource_id': datasource_id,
            'datasource_type': datasource_type,
            'datasource_name': datasource.name,
            'user_id': user_id,
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
        """
        获取用户有权限的表字段
        """
        data = []
        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            return json_error_response(DATASOURCE_MISSING_ERR)
        if not security_manager.datasource_access(datasource):
            return json_error_response(DATASOURCE_ACCESS_ERR)

        columns = [item for item in datasource.columns if item.filterable]
        for item in columns:
            if item.owners:    # 如果字段的owners属性有值，则有2种情况：如果是admin,可以访问；如果不是admin,user不在owners中，则不能访问
                if UserInfo.has_role(['Admin', 'Alpha']):
                    data.append({"name": item.column_name, "verbose_name": item.verbose_name})
                else:
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
        过滤用户有权限的表字段
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

        if UserInfo.has_all_datasource_access():
            data = datasources
        else:
            perms = UserInfo.get_view_menus('datasource_access')
            data = [item for item in datasources if item.perm in perms]

        datasources = [{"name": o.name, "id": o.id} for o in data]

        return json_success(json.dumps(datasources))

    @api
    @has_access_api
    @expose('/dealna/', methods=['POST'])
    def deal_null_value(self):
        """
        处理缺失值 
        """
        form_data, analysis = self.get_form_data()
        sk_type = form_data.get("sk_type")
        datasource_id, datasource_type = self.datasource_info(form_data)

        if not sk_type or (not datasource_id) or (not datasource_type):
            return json_error_response(REQ_PARAM_NULL_ERR % "sk_type, datasource_id, datasource_type")

        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            return json_error_response(DATASOURCE_MISSING_ERR)
        if not security_manager.datasource_access(datasource):
            return json_error_response(DATASOURCE_ACCESS_ERR)

        sk = sk_types.get(sk_type)(datasource, form_data)
        df = sk.get_df()
        null_values = df.isnull().sum()

        for key, v in null_values.to_dict().items():
            if v == 0:
                del null_values[key]
        return json_success(null_values.to_json())

    def get_xlsx_file(self, df):
        is_show_index = False  # execl表中是否显示index列

        filename = time.strftime("%Y%m%d_%H%M%S", time.localtime(time.time())) + u'.xlsx'
        filepath = os.path.join(app.config.get('SQLLAB_DATA_DIR'), filename)
        df.to_excel(filepath, index=is_show_index, encoding='utf-8', engine='xlsxwriter')
        return send_file(filepath, as_attachment=True,
                         attachment_filename=parse.quote(filename))

    @api
    @has_access_api
    @expose('/download/', methods=['POST'])
    def download(self):
        """
        下载处理之后的数据 
        """
        form_data, analysis = self.get_form_data()
        sk_type = form_data.get("sk_type")
        datasource_id, datasource_type = self.datasource_info(form_data)

        if not sk_type or (not datasource_id) or (not datasource_type):
            return json_error_response(REQ_PARAM_NULL_ERR % "sk_type, datasource_id, datasource_type")

        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            return json_error_response(DATASOURCE_MISSING_ERR)
        if not security_manager.datasource_access(datasource):
            return json_error_response(DATASOURCE_ACCESS_ERR)

        sk = sk_types.get(sk_type)(datasource, form_data)
        df = sk.get_df()
        df = sk.deal_na(df)     # 处理缺失值
        df = sk.deal_variable_box(df)      # 处理分箱
        df = sk.deal_dummy_variable(df)        # 处理亚变量
        return self.get_xlsx_file(df)


    @api
    @has_access_api
    @expose('/model/params/<name>/')
    def get_model_params(self, name):
        """
        获取模型的参数
        """
        data = []
        instance = SkModel.get_instance(name)
        if instance:
            data = instance.json_params
        return json_success(json.dumps(data))

    def allowed_file(self, filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in config.get("ALLOWED_EXTENSIONS")

    @api
    @has_access_api
    @expose('/upload/file/', methods=['GET', 'POST'])
    def upload_file(self):
        if request.method == "POST":
            if 'file' not in request.files:
                return json_error_response(u"上传文件失败：file 参数为空")
            file = request.files['file']

            if file.filename == '':
                return json_error_response(u"上传文件失败：文件名为空")
            if file and self.allowed_file(file.filename):
                filename = secure_filename(file.filename)
                new_filename = "%s_%s" %(str(uuid.uuid1()), filename)
                file.save(os.path.join(config['IMG_UPLOAD_FOLDER'], new_filename))
                payload = {"filename": new_filename, "url": config.get("IMG_UPLOAD_FOLDER")}
                return json_success(json.dumps(payload))
        return render_template("superset/import_files.html")

    @api
    @has_access_api
    @expose('/preview/code/', methods=['GET'])
    def preview_code(self):
        title = "sk_model.py"
        try:
            with open(SK_MODEL_PATH, 'r') as f:
                code = f.read()
            html_code = highlight(
                code, lexers.PythonLexer(), HtmlFormatter(linenos=True))
        except IOError as e:
            html_code = str(e)

        payload = {"title": title, "code": html_code}
        return json_success(json.dumps(payload))

    @api
    @has_access_api
    @expose('/describe/', methods=['POST'])
    def describe(self):
        """
        查看原始数据的分布
        """
        form_data, analysis = self.get_form_data()
        sk_type = form_data.get("sk_type")
        datasource_id, datasource_type = self.datasource_info(form_data)

        if not sk_type or (not datasource_id) or (not datasource_type):
            return json_error_response(REQ_PARAM_NULL_ERR % "sk_type, datasource_id, datasource_type")

        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            return json_error_response(DATASOURCE_MISSING_ERR)
        if not security_manager.datasource_access(datasource):
            return json_error_response(DATASOURCE_ACCESS_ERR)

        sk = sk_types.get(sk_type)(datasource, form_data)
        df = sk.get_df()
        html = sk.variable_describe(df)
        return json_success(html)

    @api
    @has_access_api
    @expose('/correlation_analysis/', methods=["POST"])
    def correlation_analysis(self):
        """
        查看数据相关性
        """
        form_data, analysis = self.get_form_data()
        sk_type = form_data.get("sk_type")
        datasource_id, datasource_type = self.datasource_info(form_data)

        if not sk_type or (not datasource_id) or (not datasource_type):
            return json_error_response(REQ_PARAM_NULL_ERR % "sk_type, datasource_id, datasource_type")

        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            return json_error_response(DATASOURCE_MISSING_ERR)
        if not security_manager.datasource_access(datasource):
            return json_error_response(DATASOURCE_ACCESS_ERR)

        sk = sk_types.get(sk_type)(datasource, form_data)
        df = sk.get_df()
        name, url = sk.correlation_analysis(df)
        payload = {"name": name, 'url': url}
        return json_success(json.dumps(payload))


    @api
    @has_access_api
    @expose('/run/model/', methods=["POST"])
    def run_model(self):
        form_data, analysis = self.get_form_data()
        sk_type = form_data.get("sk_type")
        datasource_id, datasource_type = self.datasource_info(form_data)

        if not sk_type or (not datasource_id) or (not datasource_type):
            return json_error_response(REQ_PARAM_NULL_ERR % "sk_type, datasource_id, datasource_type")

        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            return json_error_response(DATASOURCE_MISSING_ERR)
        if not security_manager.datasource_access(datasource):
            return json_error_response(DATASOURCE_ACCESS_ERR)

        sk = sk_types.get(sk_type)(datasource, form_data)
        log_dir_id, execl_sl, execl_bs, status, err_msg = sk.run()
        payload = {"log_dir_id": log_dir_id, "status": status, "err_msg": err_msg, "model_result_execl_sl": execl_sl,
                   "model_result_execl_bs": execl_bs}
        return json_success(json.dumps(payload))

    @api
    @has_access_api
    @expose('/log/<name>/')
    def log(self, name):


        if name not in ["code", "param", "image"]:
            return json_error_response(u"参数[name]的值错误. 取值范围[code, param, image]")

        analysis_id = request.args.get("log_dir_id")
        if not analysis_id:
            return json_error_response(u"参数[analysis_id]的值不能为空.")

        loggers = {"code": "analysis.code", "param": "analysis.param", "image": "analysis.image"}
        logger_name = loggers.get(name)
        logger = logging.getLogger(logger_name)
        handler = next((handler for handler in logger.handlers if handler.name == name), None)

        try:
            logs = handler.read(analysis_id)
        except AttributeError as e:
            logs = ["log handler {} does not support read logs.\n{}\n".format(name, str(e))]

        if not isinstance(logs, str):
            logs = logs.decode('utf-8')
        payload = logs

        images = []
        if name == "image":
            lines = logs.split('\n')
            for line in lines:
                content = line.split()
                if content and content[-1].endswith('.png'):
                    images.append(content[-1])
            payload = images

        return json_success(json.dumps(payload))

    @api
    @has_access_api
    @expose("/log/business/")
    def log_bussiness(self):
        analysis_id = request.args.get("log_dir_id")
        if not analysis_id:
            return json_error_response(u"参数[analysis_id]的值不能为空.")

        logger = logging.getLogger("analysis.param")
        handler = next((handler for handler in logger.handlers
                        if handler.name == "param"), None)

        try:
            logs = handler.read(analysis_id)
        except AttributeError as e:
            logs = ["Task log handler {} does not support read logs.\n{}\n".format("param", str(e))]

        for i, log in enumerate(logs):
            if not isinstance(log, str):
                logs[i] = log.decode('utf-8')
        return json_success(json.dumps(logs))

    @api
    @has_access_api
    @expose("/model/complete/download/", methods=["POST"])
    def download_model_data(self):
        """
        下载模型运行完成之后生成的数据
        """
        form_data, _ = self.get_form_data()
        model_result_execl_sl = form_data.get("model_result_execl_sl")
        model_result_execl_bs = form_data.get("model_result_execl_bs")
        if UserInfo.has_role([ "Admin" ]):
            filename = model_result_execl_sl
        else:
            filename = model_result_execl_bs

        directory = config.get("UPLOAD_FOLDER")
        response = make_response(send_from_directory(directory, filename, as_attachment=True))
        response.headers["Content-Disposition"] = "attachment; filename={}".format(filename)
        return response

    @api
    @has_access_api
    @expose("/table/schema/<datasource_type>/<datasource_id>/")
    def table_schema(self, datasource_type, datasource_id):
        """
        获取表结构
        """
        datasource = ConnectorRegistry.get_datasource(
            datasource_type, datasource_id, db.session)
        if not datasource:
            return json_error_response(DATASOURCE_MISSING_ERR)
        if not security_manager.datasource_access(datasource):
            return json_error_response(DATASOURCE_ACCESS_ERR)

        filterd_columns, filterd_metrics = datasource.filter_columns_metrics()
        columns = [(o.column_name, o.verbose_name or o.column_name) for o in filterd_columns]
        metrics = [(o.metric_name, o.verbose_name or o.metric_name) for o in filterd_metrics]

        payload = {"columns": columns, "metrics": metrics}
        return json_success(json.dumps(payload))


appbuilder.add_view_no_menu(Online)






