# -*- coding:utf-8 -*-
# __author__ = majing
from superset import celery_app, db
from celery.schedules import crontab
from celery_once import QueueOnce

from ..funcs import CollectInter, ValidateInter
from .models import PeriodTask, TaskRecord


@celery_app.task(base=QueueOnce, once={'graceful': True}, ignore_result=True)
def generate_task(task_id):
    """
    生成定时任务
    """
    print("task running begin ....   target: %s   type(target): %s" % (task_id, type(task_id)))

    # 添加任务记录
    record = TaskRecord(is_success=True, reason='')
    try:
        PeriodTask.update_task_status_by_id(task_id)      # 设置task的状态为running

        task_obj = PeriodTask.get_task_by_id(task_id)
        print("task running ....  value: %s" % task_obj)

        CollectInter.collect_tb_data(task_obj.id, task_obj.name, task_obj.collect_rule)
        # 校验数据
        if task_obj.validate_rule_id:
            validate_rule = task_obj.validate_rule
            types = validate_rule.types
            type_names = [item.name for item in types]
            for name in type_names:
                getattr(ValidateInter, name)(validate_rule)

        record.task_id = task_obj.id
        record.task_name = task_obj.name
    except Exception as exc:
        print("task error: %s " % str(exc))

        task_status = 'failed'
        error_msg = str(exc)

        record.is_success = False
        record.reason = str(exc)
    else:
        print("task running success ....  value: %s" % task_obj)

        task_status = 'success'
        error_msg = ''

    PeriodTask.update_task_status_by_id(task_id, task_status, error_msg)  # 设置task的状态

    TaskRecord.create_record_by_obj(record)    # 创建任务记录


def get_tasks():
    task_infos = []
    tasks = db.session.query(PeriodTask).all()
    for item in tasks:
        interval = item.interval.split()
        scheduler = crontab(minute=interval[0], hour=interval[1], day_of_month=interval[2], month_of_year=interval[3],
                            day_of_week=interval[4])
        task_infos.append((scheduler, item.id, item.name))
    return task_infos


tasks_info = get_tasks()

for key, value, name in tasks_info:
    celery_app.add_periodic_task(key, generate_task.s(value), name=name)
