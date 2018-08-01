# -*- coding:utf-8 -*-
# __author__ = majing
from superset import celery_app

from ..funcs import CollectInter, ValidateInter


@celery_app.task
def generate_task(target):
    """
    生成定时任务
    """
    # 采集数据
    if target.collect_rule_id:
        CollectInter.collect_data(target.collect_rule)

    # 校验数据
    if target.validate_rule_id:
        validate_rule = target.validate_rule
        types = validate_rule.validate_types
        type_names = [item.name for item in types]
        for name in type_names:
            getattr(ValidateInter, name)(validate_rule)


@celery_app.task
def test(arg):
    if hasattr(arg, 'a'):
        print('celery test arg param: object   ', arg.a)
    print("celery test arg param :", arg)


@celery_app.task
def add(x, y):
    print("celery add task: ", (x+y))
    return x + y

class A():
    a = 5

celery_app.add_periodic_task(30.0, test.s('world'), name='test-1',expires=10)

# celery_app.add_periodic_task(30.0, test.s('hello hello hello world'), name='test-2', expires=10)

import datetime
now = datetime.datetime.now()
add.apply_async(countdown=10, args=(4,5), expires=120)

