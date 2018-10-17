# -*- coding:utf-8 -*-
# __author__ = majing
"""
添加埋点权限：
maidian_access     项目权限
maidian_page_access     页面权限
maidian_btn_access      button权限
"""
import os
import sys
import json
import re
import datetime
from sqlalchemy.orm import load_only

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(DIR)

from superset import db
from superset.models.core_ext import MProject, MPage, MElement


def add_maidian_perms():

    projs = db.session.query(MProject)
    for pro in projs:
        if not pro.perm:
            pro.perm = '[{obj.name}].(id:{obj.id})'.format(obj=pro)
    db.session.commit()
    print("add project perms success !!!!")

    pages = db.session.query(MPage)
    for item in pages:
        if not item.perm:
            item.perm = '[{obj.name}].(id:{obj.page_id})'.format(obj=item)

    db.session.commit()
    print("add page perms success !!!!")

    btns = db.session.query(MElement)
    for item in btns:
        if not item.perm:
            item.perm = '[{obj.name}].(id:{obj.element_id})'.format(obj=item)

    db.session.commit()
    print("add btns perms success !!!!")


if __name__ == "__main__":
    add_maidian_perms()
