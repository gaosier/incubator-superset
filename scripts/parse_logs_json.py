# -*- coding:utf-8 -*-
# __author__ = majing

"""
处理金刚的日志数据  新添加了datasource_id, datasource_type 字段 
从json中解析出datasource_id
"""

import json
import os
import sys

DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(DIR)

from superset import db
from superset.models.core import Log, Slice


def parse_form_data():
    error_logs = set()

    interval = 10
    while interval > 0:
        qrys = db.session.query(Log).filter(Log.action == 'explore_json', Log.datasource_id == None).limit(1000)

        datasource_type = 'table'
        datasource_id = 0
        num = 0

        for item in qrys:
            params = json.loads(item.json)
            try:
                form_data = json.loads(params.get("form_data", "{}"))
            except:
                error_logs.add(item.id)
                continue

            try:
                if "datasource" in form_data:
                    info = form_data.get("datasource")
                    if info and '__' in info:
                        datasource_id, datasource_type = info.split("__")

                        if datasource_id == 'None':
                            datasource_id = 0

                elif "slice_id" in form_data:
                    slice_id = form_data.get("slice_id")
                    print("slice_id: %s" % slice_id)

                    slice = db.session.query(Slice).filter(Slice.id == slice_id).first()
                    if slice:
                        datasource_id = slice.datasource_id
                        datasource_type = slice.datasource_type
                    else:
                        datasource_id = 0

                else:
                    if item.json in ['{"xlsx": "true"}', '{}']:
                        datasource_id = 0
                    else:
                        error_logs.add(item.id)
                        continue

                item.datasource_id = datasource_id
                item.datasource_type = datasource_type

                db.session.merge(item)
                db.session.commit()
            except Exception as exc:
                db.session.rollback()
                print("item.action:%s  item.id:%s         Error msg: %s" % (item.action, item.id, str(exc)))
            num += 1
            print("num:%s \n" % num)

        interval -= 1
    print("json error logs: %s" % error_logs)


if __name__ == "__main__":
    parse_form_data()

