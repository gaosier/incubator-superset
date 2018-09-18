# -*-coding:utf-8-*-
from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.orm import load_only
from flask_appbuilder import Model

from superset import db


class SqlTableGroup(Model):
    __tablename__ = 'tables_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    sort_id = Column(Integer, unique=True, nullable=False, comment=u"排序序列")
    parent_id = Column(Integer, nullable=False, default=0, comment=u"父级菜单的ID")

    def __repr__(self):
        return self.name

    @classmethod
    def get_group_menus(cls, parent_id):
        query = db.session.query(cls.id, cls.name).filter(cls.parent_id == parent_id).order_by(cls.sort_id).all()
        return query


class SqlTableColumnSort(Model):
    __tablename__ = 'table_column_sort'
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer)
    table_name = Column(String(64))
    expression = Column(Text)
    remark = Column(String(64))


