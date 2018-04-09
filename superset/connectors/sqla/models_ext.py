#-*-coding:utf-8-*-
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from superset import db

from flask_appbuilder import Model


class SqlTableGroup(Model):
    __tablename__ = 'tables_group'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique = True, nullable=False)

    def __repr__(self):
        return self.name

    def get_name(group_id):
        entity = db.session.query(SqlTableGroup).get(group_id)
        return entity.name

