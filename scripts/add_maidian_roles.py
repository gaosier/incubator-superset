# -*- coding:utf-8 -*-
# __author__ = majing
"""
添加埋点角色：
1.每个项目的所有页面
2.每个项目的所有button

"""
import os
import sys
from collections import defaultdict

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(DIR)

from flask_appbuilder.security.sqla.models import PermissionView, Role, ViewMenu

from superset import db
from superset.models.core_ext import MProject, MPage, MElement


def gen_pro_page_roles(pro_id=None):
    print("begin to create page permission roles")
    pro_pages = {}
    pages = db.session.query(MPage)

    if pro_id:
        projects = [db.session.query(MProject).filter(MProject.id == MProject).first()]
    else:
        projects = db.session.query(MProject).filter(MProject.status == 0)

    # 获取每个项目的页面
    for pro in projects:
        info = []
        for page in pages:
            if pro in page.m_project:
                info.append(page.perm)
        pro_pages[pro.name] = info

    pro_view_ids = defaultdict(list)
    for key, value in pro_pages.items():
        for v in value:
            pro_view_ids[key].append(db.session.query(ViewMenu.id).filter(ViewMenu.name == v).scalar())

    # print("pro_view_ids: ", pro_view_ids)

    pro_perms = defaultdict(list)
    for key, value in pro_view_ids.items():
        perm_views = db.session.query(PermissionView).filter(PermissionView.view_menu_id.in_(value)).all()
        pro_perms[key] = perm_views
    # print("pro_perms: ", pro_perms)

    rest1 = {}
    for key, value in pro_pages.items():
        rest1[key] = len(value)
    print("rest1: ", rest1)

    rest2 = {}
    for key, value in pro_perms.items():
        rest2[key] = len(value)
    print("rest2: ", rest2)

    for key, value in pro_perms.items():
        role_name = "[%s]项目全部埋点页面" % key
        role_obj = db.session.query(Role).filter(Role.name == role_name).first()
        if role_obj:
            role_obj.permissions = value
            db.session.add(role_obj)
        else:
            role = Role()
            role.name = role_name
            role.permissions = value
            db.session.add(role)
        db.session.commit()
    print("create page role success !!!")


def gen_pro_btn_roles(pro_id=None):
    print("begin to create button permission roles")
    pro_pages = {}
    btns = db.session.query(MElement)

    if pro_id:
        projects = [db.session.query(MProject).filter(MProject.id == MProject).first()]
    else:
        projects = db.session.query(MProject).filter(MProject.status == 0)

    # 获取每个项目的buttons
    for pro in projects:
        info = []
        for ele in btns:
            mpro_pages = ele.mpage_mproject
            pro_ids = [item.mproject_id for item in mpro_pages]
            if pro.id in pro_ids:
                info.append(ele.perm)
        pro_pages[pro.name] = info

    pro_view_ids = defaultdict(list)
    for key, value in pro_pages.items():
        for v in value:
            pro_view_ids[key].append(db.session.query(ViewMenu.id).filter(ViewMenu.name == v).scalar())

    # print("pro_view_ids: ", pro_view_ids)
    pro_perms = defaultdict(list)
    for key, value in pro_view_ids.items():
        if not value:
            continue
        perm_views = db.session.query(PermissionView).filter(PermissionView.view_menu_id.in_(value)).all()
        pro_perms[key] = perm_views
    # print("pro_perms: ", pro_perms)

    rest1 = {}
    for key, value in pro_pages.items():
        rest1[key] = len(value)
    print("rest1: ", rest1)

    rest2 = {}
    for key, value in pro_perms.items():
        rest2[key] = len(value)
    print("rest2: ", rest2)

    for key, value in pro_perms.items():
        role_name = "[%s]项目全部埋点按钮" % key
        role_obj = db.session.query(Role).filter(Role.name == role_name).first()
        if role_obj:
            role_obj.permissions = value
            db.session.add(role_obj)
        else:
            role = Role()
            role.name = role_name
            role.permissions = value
            db.session.add(role)
        db.session.commit()
    print("create button role success !!!")


if __name__ == "__main__":
    gen_pro_page_roles()
    gen_pro_btn_roles()