#-*-coding:utf-8-*-
from sqlalchemy import Column, Integer, String, ForeignKey, Date,Text
from superset import db

from flask_appbuilder import Model


class SqlTableGroup(Model):
    __tablename__ = 'tables_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    sort_id = Column(Integer, unique=True, nullable=False, comment=u"排序序列")

    def __repr__(self):
        return self.name

    def get_name(group_id):
        entity = db.session.query(SqlTableGroup).get(group_id)
        return entity.name

class SqlTableColumnSort(Model):
    __tablename__ = 'table_column_sort'
    id = Column(Integer, primary_key=True)
    table_id = Column(Integer)
    table_name = Column(String(64))
    expression = Column(Text)
    remark = Column(String(64))


