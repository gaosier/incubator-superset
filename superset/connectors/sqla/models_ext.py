# -*-coding:utf-8-*-
from collections import defaultdict

from sqlalchemy import Column, Integer, String, Text
from flask_appbuilder import Model

from superset import db


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


class SqlTableColumnVal(Model):
    """
    需要特殊控制的字段的值
    """
    __tablename__ = "table_column_val"
    id = Column(Integer, primary_key=True)
    datasource_type = Column(String(10), nullable=False, comment=u"表的类型")
    datasource_id = Column(Integer, nullable=False, comment=u"表的ID")
    user_id = Column(Integer, nullable=False, comment=u"用户ID")
    col = Column(String(50), nullable=False, comment=u"字段的名字")
    val = Column(String(100), nullable=False, comment=u"字段的值")

    @classmethod
    def is_perm_control_col(cls, table_type, table_id, col):

        qry = db.session.query().filter(cls.datasource_type == table_type, cls.datasource_id == table_id,
                                              cls.col == col).count()

        return True if qry > 0 else False

    @classmethod
    def is_perm_control_table(cls, table_type, table_id):
        count = db.session.query(cls).filter(cls.datasource_type == table_type, cls.datasource_id == table_id).count()

        return True if count > 0 else False

    @classmethod
    def has_perm_col(cls, table_type, table_id, col, user_id):
        qry = db.session.query(cls).filter(cls.datasource_type == table_type, cls.datasource_id == table_id,
                                              cls.col == col, cls.user_id == user_id).count()

        return True if qry > 0 else False

    @classmethod
    def perm_user_col_vals(cls, table_type, table_id, col, user_id):
        """
        用户当前字段有权限的值
        """
        qry = db.session.query(cls.val).filter(cls.datasource_type == table_type, cls.datasource_id == table_id,
                                           cls.col == col, cls.user_id == user_id).all()
        qry = [item[0] for item in qry]
        return qry

    @classmethod
    def perm_table_user_col_vals(cls, table_type, table_id, user_id):
        """
        当前的表和user是否在需要特殊控制
        """
        data = defaultdict(list)
        qrys = db.session.query(cls.col, cls.val).filter(cls.datasource_type == table_type, cls.datasource_id == table_id,
                                           cls.user_id == user_id)

        for name, val in qrys:
            if val not in data[name]:
                data[name].append(val)

        return data

