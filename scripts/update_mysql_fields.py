# -*- coding:utf-8 -*-
# __author__ = majing

"""
修改数据库字段   新版数据库和老版数据库 slice params 字段差异
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
from superset.models.core import Slice


def deal_field():
    result = db.session.query(Slice).options(load_only("id", "slice_name", "params"))
    for item in result:
        try:
            params = json.loads(item.params)
        except Exception as exc:
            print("error: exc: %s    slice_name: %s    params: %s" % (exc, item.slice_name, item.params))

        else:
            time_period = params.get('time_period')
            if not time_period:
                continue
            if '-' in time_period:
                print("slice_name: %s   time_period: %s" % (item.slice_name, time_period))
                split_times = re.findall(r'\d+', time_period)
                if split_times:
                    split_times = list(map(lambda x: int(x), split_times))
                    since = datetime.datetime(split_times[0], split_times[1], split_times[2]).strftime('%Y-%m-%dT%H:%M:%S')
                    until = datetime.datetime(split_times[3], split_times[4], split_times[5], 23, 59, 59).strftime('%Y-%m-%dT%H:%M:%S')
                    params['since'] = since
                    params['until'] = until
                    try:
                        item.params = json.dumps(params)
                        db.session.commit()
                    except Exception as exc:
                        print('session update exc error: %s  slice_name: %s' % (exc, item.slice_name))
                        db.session.rollback()

def update_field(id):
    slice = db.session.query(Slice).filter(Slice.id==id).first()
    print("slice: ", slice)
    params = json.loads(slice.params)
    if params.get('granularity_sqla'):
        params['granularity_sqla'] = "lesson_begin_time"
        try:
            slice.params = json.dumps(params)
            db.session.commit()
        except Exception as exc:
            print('session update exc error: %s  slice_name: %s' % (exc, slice.slice_name))
            db.session.rollback()


if __name__ == "__main__":
    deal_field()