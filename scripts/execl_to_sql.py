# -*- coding:utf-8 -*-
# __author__ = majing

"""
字段控制到值  把execl 转换成sql语句
"""
import os
import sys

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(DIR)

import xlrd
from superset import db,security_manager
from superset.connectors.sqla.models import SqlaTable

if len(sys.argv) > 1:
    file_name = sys.argv[1]
    sheet_name = sys.argv[2]
else:
    raise ValueError("请输入文件名和sheet名")

workbook = xlrd.open_workbook(file_name)
table = workbook.sheet_by_name(sheet_name)
nrows = table.nrows


def get_infos():
    table_names = set()
    user_names = set()
    for i in range(nrows):
        content = table.row_values(i)
        if content[0] == u'\u8868':
            continue
        if content[0] and content[0].strip():
            table_names.add(content[0])

        if content[1]:
            email = content[1].split("：")

            if len(email) == 2:
                email = email[1]
            user_names.add(email)

    return table_names, user_names


def get_tables_id(tab_names):
    """
    获取table的ID 
    """
    qrys = db.session.query(SqlaTable.table_name, SqlaTable.id).filter(SqlaTable.table_name.in_(tab_names))
    qrys = {item[0]:item[1] for item in qrys}
    return qrys


def get_users_id(user_names):
    """
    获取用户的ID
    :param user_names: 
    :return: 
    """
    User = security_manager.user_model
    qrys = db.session.query(User.email, User.id).filter(User.email.in_(user_names))
    qrys = {item[0]: item[1] for item in qrys}
    return qrys


def get_table_user_ids():
    table_names, user_names = get_infos()
    table_ids = get_tables_id(table_names)
    user_ids = get_users_id(user_names)
    return table_ids, user_ids


def split_vals(val):
    if '，' in val:
        val = val.split('，')
    elif ',' in val:
        val = val.split(',')
    else:
        val = [val]
    return val


def split_email(email):
    if ':' in email:
        val = email.split(":")
    elif '：' in email:
        val = email.split("：")
    else:
        val = [email]

    if len(val) == 2:
        val = val[1]
    else:
        val = None
    return val


def gen_sqls():
    table_ids, user_ids = get_table_user_ids()
    print("table_ids: ", table_ids)
    print("user_ids: ", user_ids)

    count = 0
    with open('col_val.sql', 'w+') as f:

        for i in range(1, nrows):
            content = table.row_values(i)
            if content[0] and content[0].strip():
                table_name = content[0]
                tab_id = table_ids.get(table_name)

            if content[1]:
                email = split_email(content[1])
                user_id = user_ids.get(email)

            val = []
            if content[2]:
                col = content[2]
                val = content[3]
                val = split_vals(val)

            for item in val:
                sql = "insert into table_column_val(datasource_type, datasource_id, user_id, col, val) " \
                      "values ('%s', %s, %s, '%s', '%s');\n" % ('table', int(tab_id), int(user_id), col, item)

                f.write(sql)
                count += 1

            val_2 = []
            if content[4]:
                col_1 = content[4]
                val_2 = content[5]
                val_2 = split_vals(val_2)

            for item in val_2:
                sql = "insert into table_column_val(datasource_type, datasource_id, user_id, col, val) " \
                      "values ('%s', %s, %s, '%s', '%s');\n" % ('table', int(tab_id), int(user_id), col_1, item)
                f.write(sql)
                count += 1
        f.write("# ========total:%s ====================" % count)

if __name__ == "__main__":
    gen_sqls()









