from flask_appbuilder.security.sqla.models import User
from sqlalchemy import Column, Integer, ForeignKey, String, Sequence, Table,Enum
from sqlalchemy.orm import relationship, backref
from flask_appbuilder import Model
from . import config
class MyUser(User):
    department = Column(Enum(*getattr(config,'MY_USER_DEPARTMENT',[]),nullable=True))