# -*- coding:utf-8 -*-
# __author__ = majing
"""
字段值控制功能  用户只能看到表字段的某一些值
"""
import json
from flask import render_template, request
from flask_appbuilder import BaseView
from flask_appbuilder.baseviews import expose
from superset import appbuilder, db
from superset.views.base import json_success, api
from superset.connectors.sqla.models import SqlaTable
from superset.connectors.sqla.models_ext import SqlTableColumnVal
from superset.views.base_ext import login_required
from superset.connectors.connector_registry import ConnectorRegistry
from flask_appbuilder.security.sqla.models import User
from superset.exceptions import SupersetException


class ValuePermView(BaseView):

    def check_params(self, form_data):
        for key, value in form_data.items():
            if not value:
                raise SupersetException("参数%s的值不能为空" % key)

    @expose('/get/template/', methods=['GET'])
    @login_required
    def get_template(self):
        return render_template('', entry='')

    @api
    @expose('/list/', methods=['POST'])
    @login_required
    def list(self):
        """
        列表 
        """
        search = json.loads(request.form.get('search')) if request.form.get('search') else {}
        page = int(request.form.get('page'))
        page_size = int(request.form.get('page_size'))

        data, total = SqlTableColumnVal.get_lists(search, page, page_size)
        payload = {"data": data, "search_column": SqlTableColumnVal.search_columns(), "total": total}
        return json_success(json.dumps(payload))

    @api
    @expose('/tables/', methods=['GET'])
    @login_required
    def tables(self):
        """
        获取所有的表的ID，名字
        :return: 
        """
        cols = ('id', 'verbose_name')
        tables = ConnectorRegistry.get_model_cols(cols, SqlaTable, session=db.session)
        return json_success(json.dumps(tables))

    @api
    @expose('/users/', methods=['GET'])
    @login_required
    def users(self):
        """
        获取所有的用户ID，名字 
        """
        cols = ('id', 'last_name', 'first_name')
        users = ConnectorRegistry.get_model_cols(cols, User, session=db.session)

        data = []
        for item in users:
            data.append([item[0], item[1]+item[2]])

        return json_success(json.dumps(data))

    @api
    @expose('/table/cols/', methods=['POST'])
    @login_required
    def table_cols(self):
        """
        获取表的列
        """
        pk = request.form.get('pk')
        if not pk:
            raise SupersetException(u"pk不能为空")

        table = ConnectorRegistry.get_datasource('table', pk, db.session)

        data = [item.verbose_name or item.column_name for item in table.columns] if table else []
        return json_success(json.dumps(data))

    @api
    @expose('/column/vals/', methods=['POST'])
    @login_required
    def column_vals(self):
        """
        获取列的值 
        """
        pk = request.form.get('pk')
        col = request.form.get('col')

        if not pk:
            raise SupersetException(u"pk不能为空")

        table = ConnectorRegistry.get_datasource('table', pk, db.session)
        data = table.values_for_column(col) if table else []
        return json_success(json.dumps(data))

    @api
    @expose('/add/', methods=['POST'])
    @login_required
    def add(self):
        """
        添加信息 
        """
        self.check_params(request.form)
        tab_id = request.form.get('tab_id')
        user_id = request.form.get('user_id')
        col_vals = json.loads(request.form.get('col_vals')) if request.form.get('col_vals') else {}

        for key, value in col_vals.items():
            instance = SqlTableColumnVal()
            instance.datasource_id = tab_id
            instance.user_id = user_id
            instance.col = key
            instance.val = value

            db.session.add(instance)
            db.session.commit()
        return json_success(json.dumps({"msg": u"添加成功"}))

    @api
    @expose('/edit/<pk>/', methods=['POST'])
    @login_required
    def edit(self, pk):
        """
        编辑
        """
        instance = SqlTableColumnVal.get_instance(pk)

        self.check_params(request.form)
        col = request.form.get('col')
        val = request.form.get('val')

        instance.col = col
        instance.val = val

        db.session.add(instance)
        db.session.commit()
        return json_success(json.dumps({"msg": u"编辑成功"}))

    @api
    @expose('/delete/', methods=['POST'])
    @expose('/delete/<pk>/', methods=['GET'])
    @login_required
    def delete(self, pk=None):
        """
        删除
        """
        if request.method == 'GET':
            instance = SqlTableColumnVal.get_instance(int(pk))
            if instance:
                db.session.delete(instance)
        else:
            pks = request.form.get('pks')
            pks = pks.split(',') if ',' in pks else [pks]
            for pk in pks:
                instance = SqlTableColumnVal.get_instance(pk)
                if instance:
                    db.session.delete(instance)
        db.session.commit()
        return json_success(json.dumps({"msg": u"删除成功"}))


appbuilder.add_separator('Manage')
appbuilder.add_view(ValuePermView, 'Column Value Perm', label=u"字段值控制", category='Manage', icon='fa-archive',
                    href='/valuepermview/get/template/'
                    )
