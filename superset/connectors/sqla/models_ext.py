# -*-coding:utf-8-*-
import json
import logging
from collections import defaultdict

from sqlalchemy import Column, Integer, String, Text, UniqueConstraint, ForeignKey, and_, func
from sqlalchemy.orm import relationship
from flask_appbuilder import Model

from superset import db, security_manager
from superset.models.helpers import AuditMixinNullable


class SqlTableGroup(Model):
    """
    数据中心分类
    """
    __tablename__ = 'tables_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    sort_id = Column(Integer, unique=True, nullable=False, comment=u"排序序列")
    parent_id = Column(Integer, nullable=False, default=0, comment=u"父级菜单的ID")

    def __repr__(self):
        return self.name

    @classmethod
    def get_group_menus(cls, parent_id):
        query = db.session.query(cls.id, cls.name).filter(cls.parent_id == parent_id).\
            order_by(cls.sort_id).all()
        data = [{"id": item[0], "name": item[1]} for item in query]
        return data

    @classmethod
    def get_name(cls, group_id):
        query = db.session.query(cls.name).filter(cls.id == group_id).scalar()
        return query

    @classmethod
    def get_groups_by_ids(cls, ids):
        query = db.session.query(cls.id, cls.name).filter(cls.id.in_(ids)).order_by(cls.sort_id).all()
        data = [{"id": item[0], "name": item[1]} for item in query]
        return data

    @classmethod
    def all_group_names(self):
        qrys = db.session.query(SqlTableGroup.id, SqlTableGroup.name).all()
        data = {item[0]:item[1] for item in qrys}
        return data


class SqlTableColumnSort(Model):
    """
    需要特殊排序的表
    """
    __tablename__ = 'table_column_sort'
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer)
    table_name = Column(String(64))
    expression = Column(Text)
    remark = Column(String(64))

    @classmethod
    def get_sort_columns(cls, table_id, table_name):
        qry = db.session.query(SqlTableColumnSort).filter(SqlTableColumnSort.table_id == table_id,
                SqlTableColumnSort.table_name == table_name)
        if qry.count() == 0:
            logging.info('表{0}-{1}未匹配到配置项'.format(table_id, table_name))
            return None
        col = qry.first()
        exp = None
        try:
            exp = json.loads(col.expression)
        except:
            logging.info('表{0}的排序参数不是合法的json'.format(table_name))
        return exp


class SqlTableColumnVal(Model, AuditMixinNullable):
    """
    需要特殊控制的字段的值
    """
    __tablename__ = "table_column_val"
    __table_args__ = (UniqueConstraint('datasource_id', 'user_id', 'col'), )
    id = Column(Integer, primary_key=True)
    datasource_id = Column(Integer, ForeignKey('tables.id'), nullable=False, comment=u"表的ID")
    datasource = relationship("SqlaTable", backref=db.backref("columnvals", cascade="all, delete-orphan"))
    user_id = Column(Integer, ForeignKey('ab_user.id'), comment=u"用户ID")
    user = relationship(security_manager.user_model, foreign_keys=[user_id])
    col = Column(String(50), nullable=False, comment=u"字段的名字")
    val = Column(String(500), nullable=False, comment=u"字段的值")

    @classmethod
    def search_columns(cls):
        return {'table_name': u"表名", 'username':"用户名"}

    @classmethod
    def is_perm_control_col(cls, table_id, col):

        qry = db.session.query().filter(cls.datasource_id == table_id, cls.col == col).count()

        return True if qry > 0 else False

    @classmethod
    def is_perm_control_table(cls, table_id):
        count = db.session.query(cls).filter(cls.datasource_id == table_id).count()

        return True if count > 0 else False

    @classmethod
    def has_perm_col(cls, table_id, col, user_id):
        qry = db.session.query(cls).filter(cls.datasource_id == table_id, cls.col == col,
                                           cls.user_id == user_id).count()

        return True if qry > 0 else False

    @classmethod
    def perm_user_col_vals(cls, table_id, col, user_id):
        """
        用户当前字段有权限的值
        """
        qry = db.session.query(cls.val).filter(cls.datasource_id == table_id, cls.col == col, cls.user_id == user_id)
        qry = [item[0] for item in qry]
        return qry

    @classmethod
    def perm_table_user_col_vals(cls, table_id, user_id):
        """
        当前的表和user是否在需要特殊控制
        """
        data = defaultdict(list)
        qrys = db.session.query(cls.col, cls.val).filter(cls.datasource_id == table_id, cls.user_id == user_id)

        for name, val in qrys:
            if name not in data:
                vals = val.split(',') if ',' in val else [val]
                data[name].extend(vals)

        return data

    def get_username(self, user):
        return "%s%s" % (user.last_name, user.first_name)

    @classmethod
    def get_lists(cls, search, page, page_size):
        """
        :param search: {"table_name": '', "username": ''}
        :param page: 
        :param page_size: 
        """
        from .models import SqlaTable

        User = security_manager.user_model
        data = []
        qrys = db.session.query(cls)

        if 'table_name' in search and 'username' in search:
            query = qrys.join(SqlaTable).filter(SqlaTable.table_name.contains(search.get('table_name'))).\
                join(User).filter(User.username.contains(search.get('username')))
        elif 'table_name' in search:
            query = qrys.join(SqlaTable).filter(SqlaTable.table_name.contains(search.get('table_name')))
        elif 'username' in search:
            query = qrys.join(User).filter(User.username.contains(search.get('username')))
        else:
            query = qrys

        total = query.count()

        query = query.limit(page_size).offset((page-1)*page_size)

        for qry in query:
            info = {}
            info['id'] = qry.id
            info['table_name'] = qry.datasource.table_name
            info['tab_id'] = qry.datasource_id
            info['user_id'] = qry.user_id
            info['verbose_name'] = qry.datasource.verbose_name
            info['username'] = cls.get_username(qry, qry.user)
            info['col'] = qry.col
            info['val'] = qry.val
            info['creator'] = cls.get_username(qry, qry.created_by) if qry.created_by else ''
            info['modify'] = qry.changed_on.strftime('%Y-%m-%d %H:%M:%S') if qry.changed_on else ''
            data.append(info)
        return data, total

    @classmethod
    def get_instance(cls, pk):
        return db.session.query(cls).filter(cls.id == pk).first()


