# -*-coding:utf-8-*-
import datetime
import json
import logging
import os
import re
from urllib.parse import quote
import pandas as pd
from flask import (
     g, request, redirect, flash, Response, render_template, Markup,
    abort, url_for,send_from_directory,send_file)
from flask_babel import gettext as __

from superset import (
    app, appbuilder, cache, db, results_backend, security, sql_lab, utils,
    viz, utils_ext, security_manager,db
)
from sqlalchemy import create_engine
from wtforms.validators import DataRequired, Regexp
from flask_appbuilder.models.sqla.filters import BaseFilter

from flask_appbuilder.security.decorators import has_access, has_access_api
import superset.models.core as models
from superset.models.core_ext import MPage,MpageMproject,MElement,JingYouUser,MProject
from superset.models.sql_lab import Query
from .core import get_datasource_access_error_msg
from flask_appbuilder import expose, SimpleFormView
from superset.fab.models.sqla.interface import SupersetSQLAInterface as SQLAInterface
from .base import (
    api, BaseSupersetView, CsvResponse, DeleteMixin,
    generate_download_headers, get_error_msg, get_user_roles,
    json_error_response, SupersetFilter, SupersetModelView, YamlExportMixin,
)

from ..connectors.sqla.models import SqlaTable


config = app.config
stats_logger = config.get('STATS_LOGGER')
log_this = models.Log.log_this
sqllab_data_dir = config.get('SQLLAB_DATA_DIR')


class SupersetExt(BaseSupersetView):
    @has_access
    @expose("/xlsx/<client_id>")
    @log_this
    def xlsx(self, client_id):
        """Download the query results as xlsx."""
        logging.info("Exporting XLSX file [{}]".format(client_id))
        query = (
            db.session.query(Query)
            .filter_by(client_id=client_id)
            .one()
        )

        rejected_tables = security_manager.rejected_datasources(
            query.sql, query.database, query.schema)
        if rejected_tables:
            flash(get_datasource_access_error_msg('{}'.format(rejected_tables)))
            return redirect('/')
        blob = None
        if results_backend and query.results_key:
            logging.info(
                "Fetching XLSX from results backend "
                "[{}]".format(query.results_key))
            blob = results_backend.get(query.results_key)
        filename = query.name + u'.xlsx'
        filepath = os.path.join(sqllab_data_dir, filename)
        if blob:
            logging.info("Decompressing")
            json_payload = utils.zlib_decompress_to_string(blob)
            obj = json.loads(json_payload)
            columns = [c['name'] for c in obj['columns']]
            df = pd.DataFrame.from_records(obj['data'], columns=columns)
            logging.info("Using pandas to convert to XLSX")
            df.to_excel(filepath, index=False, encoding='utf-8', engine='xlsxwriter')
        else:
            logging.info("Running a query to turn into XLSX")
            sql = query.select_sql or query.executed_sql
            df = query.database.get_df(sql, query.schema)
            # TODO(bkyryliuk): add compression=gzip for big files.
            df.to_excel(filepath, index=False, encoding='utf-8', engine='xlsxwriter')
        return send_file(filepath, as_attachment=True, 
                attachment_filename=quote(filename))


appbuilder.add_view_no_menu(SupersetExt)

class TableColumnFilter(SupersetFilter):
    """
    用于过滤是用户和admin账户创建的列和指标
    """
    def apply(self, query, func):  # noqa
        if self.has_all_datasource_access():
            return query
        admin_user_list=utils_ext.get_admin_id_list(db)
        from sqlalchemy import or_
        return query.filter(or_(self.model.created_by==g.user,self.model.created_by_fk.in_(admin_user_list),self.model.created_by_fk==None))


class JingYouModelView(SupersetModelView):
    datamodel = SQLAInterface(JingYouUser)
    datamodel.add_integrity_error_message='用户名重复'
    list_title = '用户列表'
    show_title = '用户信息'
    add_title = '添加用户'
    edit_title = '编辑用户'
    list_columns = ['uname', 'password','ip','port','updated','subject_product','get_status','comment']
    add_columns = [ 'uname', 'password','ua', 'cookies','ip','port','comment']
    search_columns = ('uname','ip','port')
    show_columns = [
        'uname', 'password',
        'ua', 'cookies','ip','port','updated','status']
    edit_columns = [ 'password','ua','cookies','ip','port','comment']
    description_columns={
        'status':"1表示未发生变化，2表示已发生变化"
    }
    label_columns={
        'uname':"用户名",
        'password':"密码",
        'ua':"浏览器ua",
        'cookies':'浏览器cookie',
        'ip':'外网ip',
        'port':'端口',
        'updated':'更新时间',
        'get_status':'状态',
        'comment':"备注",
        'subject_product': '学科'
    }
    def pre_update(self,obj):
        sql="select cookies from jingyou_user WHERE uname = '%s'"%(obj.uname)
        item = db.session.execute(sql).first()
        if item[0] !=obj.cookies:
            obj.status=2


class ProjectFilter(SupersetFilter):
    def apply(self, query, func):  # noqa
        if self.has_role(['Admin', 'Alpha']):
            return query
        perms = self.get_view_menus('maidian_access')
        return query.filter(MProject.perm.in_(perms))


class MProjectView(SupersetModelView):
    datamodel = SQLAInterface(MProject)
    validators_columns = {'id': [Regexp(r'^[a-z]+$', message=u'项目ID不合法,请以项目名称为项目ID,项目名称中仅包含(a-z)中的字符')]}
    list_title = '项目列表'
    show_title = '项目信息'
    add_title = '添加项目'
    edit_title = '编辑项目'

    add_columns = ['id', 'name', 'name_type', 'full_id', 'describe', 'status']
    show_columns = ['id', 'name', 'name_type', 'full_id', 'describe', 'status']
    list_columns = ['id', 'name', 'project_type_link', 'get_status', 'page_or_element_button']
    edit_columns = ['id', 'name', 'full_id', 'describe', 'status']

    search_columns = ['id', 'name', 'name_type']
    order_columns = ['id']
    base_filters = [ ['id', ProjectFilter, '']]

    label_columns = {
        'id': "项目id",
        'name': "项目名称",
        'name_type': "项目分类",
        'full_id': '全称',
        'describe': '描述',
        'pm_owner': '产品负责人',
        'tech_owner': '技术负责人',
        'project_link':'项目名称',
        'project_type_link':'项目分类',
        'get_status': '状态',
        'status': '状态(勾选表示禁用)',
        'page_or_element_button':'操作'
    }

    def pre_add(self, obj):
        # 去掉string的空格
        string_columns = self.datamodel.get_all_string_columns()
        for col in string_columns:
            value = getattr(obj, col)
            if value:
                setattr(obj, col, value.strip())

    def pre_update(self, obj):
        # 去掉string的空格
        string_columns = self.datamodel.get_all_string_columns()
        for col in string_columns:
            value = getattr(obj, col)
            if value:
                setattr(obj, col, value.strip())


appbuilder.add_view(
    MProjectView,
    "M Project View",
    label="埋点管理",
    icon="fa-envelope",
    category="",
    category_icon='',)


class MPageFilter(SupersetFilter):
    def apply(self, query, func):  # noqa
        if self.has_role(['Admin', 'Alpha']):
            return query
        perms = self.get_view_menus('maidian_page_access')
        return query.filter(MPage.perm.in_(perms))


class MPageView(SupersetModelView):
    datamodel = SQLAInterface(MPage)
    validators_columns = {"page_id": [Regexp(r'^[0-9A-Za-z_]+$', message=u'页面ID不合法,请输入字母数字下划线的组合')],
                          "name": [DataRequired()], "m_project": [DataRequired()]}
    list_title = '页面列表'
    show_title = '页面详情'
    add_title = '添加页面信息'
    edit_title = '编辑页面信息'
    add_columns = ['page_id','m_project','menu1','menu2','menu3','menu4','name','url','m_describe','del_status','up1',
                   'pp1','pp2','pp3','pp4','pp5']
    list_columns = ['page_id','menu1','menu2','menu3','mproject_name','name','update_time','get_del_status','melement_url_btn']
    search_columns = ['page_id','m_project','menu1','menu2','menu3','menu4','name','url','del_status']
    edit_columns = ['page_id','m_project','menu1','menu2','menu3','menu4','name','url','m_describe','del_status','up1',
                   'pp1','pp2','pp3','pp4','pp5']
    show_columns = edit_columns + ['status', 'create_time', 'update_time']
    base_filters = [['id', MPageFilter, lambda: []]]
    order_columns = ['page_id']
    description_columns = {
        'status': "1表示未修改，2表示已修改",
        'del_status':"勾选表示已删除",
        'm_process':'1未开始,2开发中,3测试中,4已上线'
    }
    label_columns = {
        'page_id': "页面id",
        'mproject_name': "所属项目名称",
        'm_project': "所属项目名称",
        'menu1': "一级菜单",
        'menu2': '二级菜单',
        'menu3': '三级菜单',
        'menu4': '四级菜单',
        'name': '页面名称',
        'url': '页面地址',
        'url_link': '页面地址',
        'm_describe': '页面描述',
        'status':'状态',
        'get_status':'状态',
        'del_status':'是否删除',
        'get_del_status':'是否删除',
        'up1': '用户扩展属性(up1)',
        'up2': '用户扩展属性2(up2)',
        'up3': '用户扩展属性3(up3)',
        'up4': '用户扩展属性4(up4)',
        'up5': '用户扩展属性5(up5)',
        'pp1':'页面扩展属性1(pp1)',
        'pp2':'页面扩展属性2(pp2)',
        'pp3':'页面扩展属性3(pp3)',
        'pp4':'页面扩展属性4(pp4)',
        'pp5':'页面扩展属性5(pp5)',
        'm_process':'进度',
        'version':'版本号',
        'melement_url_btn':'点击埋点链接',
        'update_time':'更新时间'
    }
    post_update_flag=False

    def pre_update(self,obj):
        columns_name=[]
        for i in obj.__table__.columns:
            tab,col=str(i).split(".")
            if col not in ('update_time','create_time'):
                columns_name.append(col)
        sql1="select `%s` from m_page WHERE id = %s"%('`,`'.join(columns_name),obj.id)
        item1 = db.session.execute(sql1).first()
        for ind,col in enumerate(columns_name):
                if getattr(obj,col) != item1[ind]:
                    obj.status=True
                    break
        sql2="select mproject_id from mpage_mproject WHERE mpage_id = %s"%(obj.id)
        item2 =sorted([i[0] for i in db.session.execute(sql2)])
        new_mproject_id=sorted([i.id for i in obj.m_project])
        if item2 != new_mproject_id:
            self.post_update_flag=True

            obj.status = True

        # 去掉string的空格
        string_columns = self.datamodel.get_all_string_columns()
        for col in string_columns:
            value = getattr(obj, col)
            if value:
                setattr(obj, col, value.strip())

    def pre_add(self, obj):
        """
        处理前端页面的数据
        """
        # 去掉string的空格
        string_columns = self.datamodel.get_all_string_columns()
        for col in string_columns:
            value = getattr(obj, col)
            if value:
                setattr(obj, col, value.strip())

    def post_update(self,obj):
        if self.post_update_flag:
            mpage_mproject_list = db.session.query(models.MpageMproject).filter_by(mpage_id=obj.id)
            url = '/melementview/list/?'
            flag = False
            for i in mpage_mproject_list:
                url += '_flt_0_mpage_mproject=%s&' % i.id
                if not flag:
                    if len(db.session.query(models.MElement).filter(models.MElement.mpage_mproject.contains(i)).all()) != 0:
                        flag=True
            if flag:
                obj.melement_url=url
            else:
                obj.melement_url = None
            db.session.commit()
            self.post_update_flag=False

appbuilder.add_view_no_menu(MPageView)


class ElementFilter(SupersetFilter):
    def apply(self, query, func):  # noqa
        if self.has_role(['Admin', 'Alpha']):
            return query
        perms = self.get_view_menus('maidian_btn_access')
        return query.filter(MElement.perm.in_(perms))


class MElementView(SupersetModelView):
    datamodel = SQLAInterface(MElement)
    validators_columns = {"element_id": [Regexp(r'^[0-9A-Za-z_]+$', message=u'按钮ID不合法,请输入字母数字下划线的组合')],
                          "name": [DataRequired()]}
    list_title = '点击列表'
    show_title = '点击详情'
    add_title = '添加点击信息'
    edit_title = '编辑点击信息'
    add_columns=['element_id','mpage_mproject','name','del_status','pp1','pp2','pp3','pp4','pp5']
    list_columns=['element_id','mpage_mproject_name','name','get_del_status','update_time']
    search_columns=['element_id','mpage_mproject','name','del_status']
    edit_columns = add_columns
    show_columns = add_columns+['status','create_time','update_time']
    base_filters = [['id', ElementFilter, '']]

    description_columns = {
        'status': "1表示未修改，2表示已修改",
        'del_status': "勾选表示删除",
        'm_process': '1未开始,2开发中,3测试中,4已上线',
         'pp1': '增加点击行为的一些扩展属性',
    }
    label_columns = {
        'element_id': "按钮id",
        'mpage_mproject': "所属项目及页面",
        'mpage_mproject_name': "所属项目及页面",
        'name': '按钮名称',
        'status': '状态',
        'get_status': '状态',
        'del_status': '是否删除',
        'm_process': '进度',
        'version': '版本号',
        'get_del_status':'是否删除',
        'update_time': '更新时间'
    }

    def pre_update(self,obj):
        columns_name=[]
        for i in obj.__table__.columns:
            tab,col=str(i).split(".")
            if col not in ('update_time','create_time'):
                columns_name.append(col)
        sql1="select `%s` from m_element WHERE id = %s"%('`,`'.join(columns_name),obj.id)
        item1 = db.session.execute(sql1).first()
        for ind,col in enumerate(columns_name):
                if getattr(obj,col) != item1[ind]:
                    obj.status=True
                    return None

        sql2="select mpage_mproject_id from melement_mpage_mproject WHERE melement_id = %s"%(obj.id)
        item2 =sorted([i[0] for i in db.session.execute(sql2)])
        new_item_id=sorted([i.id for i in obj.mpage_mproject])
        if item2 != new_item_id:
            obj.status=True

        # 去掉string的空格
        string_columns = self.datamodel.get_all_string_columns()
        for col in string_columns:
            value = getattr(obj, col)
            if value:
                setattr(obj, col, value.strip())

    def pre_add(self, obj):
        """
        处理前端页面的数据
        """
        # 去掉string的空格
        string_columns = self.datamodel.get_all_string_columns()
        for col in string_columns:
            value = getattr(obj, col)
            if value:
                setattr(obj, col, value.strip())

    def post_add(self,obj):
        for i in obj.mpage_mproject:
            page_obj=db.session.query(MPage).filter_by(id=i.mpage_id).first()
            if not page_obj.melement_url:
                page_obj.melement_url = '/melementview/list/?_flt_0_mpage_mproject=%s&' % i.id
                db.session.commit()
            else:
                if i.id in page_obj.melement_url:
                    pass
                else:
                    page_obj.melement_url+='_flt_0_mpage_mproject=%s&'%i.id
                    db.session.commit()


appbuilder.add_view_no_menu(MElementView)

# 北校用户登录热力图
appbuilder.add_link(
    __('Login Map'),
    href='/loginmap/my_queries/',
    icon='fa-map',
    category='')


class LoginMap(BaseSupersetView):
    @expose('/my_queries/')
    def my_queries(self):
        return self.render_template('superset/beixiao/base.html')


class LoadMap(BaseSupersetView):
    @expose('/my_queries/', methods=['GET', 'POST'])
    def my_queries(self):
        """
        查询数据
        :return: 
        """
        rest = []
        table_name = 'dm_beixiao_page'
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')

        if start_time and end_time:
            start_time = datetime.datetime.strptime(start_time, '%Y/%m/%d').strftime('%Y%m%d')
            end_time = datetime.datetime.strptime(end_time, '%Y/%m/%d').strftime('%Y%m%d')
        else:
            start_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
            end_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')

        table = db.session.query(SqlaTable).filter(SqlaTable.table_name == table_name).first()
        if table:
            database = table.database
            engine = database.get_sqla_engine()
            result = engine.execute(
                'select lng, lat, count(*) as num from %s where day<= "%s" and day>= "%s" group by lng, lat' % (
                    table_name, end_time, start_time,
                ))
            rows = result.fetchall()
            for item in rows:
                data = {}
                data['count'] = item[2]
                data['coordinate'] = [item[0], item[1]]
                rest.append(data)

        return self.render_template('superset/beixiao/map.html', data=json.dumps(rest), total=len(rest))

appbuilder.add_view_no_menu(LoginMap)
appbuilder.add_view_no_menu(LoadMap)
