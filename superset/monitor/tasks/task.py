# -*- coding:utf-8 -*-
# __author__ = majing
from superset import celery_app, db
from celery.schedules import crontab

from ..funcs import CollectInter, ValidateInter


@celery_app.task
def generate_task(target):
    """
    生成定时任务
    """
    # 采集数据
    session = db.session
    task_obj = None

    print("task running begin ....")
    # if target:
    #     task_obj = session.query(PeriodTask).filter(id == target).first()
    #
    # if task_obj:
    #     CollectInter.collect_tb_data(task_obj.id, task_obj.name, target.collect_rule)
    #     # 校验数据
    #     if task_obj.validate_rule_id:
    #         validate_rule = task_obj.validate_rule
    #         types = validate_rule.validate_types
    #         type_names = [item.name for item in types]
    #         for name in type_names:
    #             getattr(ValidateInter, name)(validate_rule)
    print("task running success ....")


def set_tasks(mapper, connection, target):  # noqa
    interval = target.interval.split()
    scheduler = crontab(minute=interval[0], hour=interval[1], day_of_month=interval[2], month_of_year=interval[3],
                        day_of_week=interval[4])

    celery_app.add_periodic_task(scheduler, generate_task.s(target.id))
