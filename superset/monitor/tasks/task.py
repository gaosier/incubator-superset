# -*- coding:utf-8 -*-
# __author__ = majing
from superset import celery_app, db
from celery.schedules import crontab

from ..funcs import CollectInter, ValidateInter
from .models import PeriodTask, TaskRecord


@celery_app.task
def generate_task(target):
    """
    生成定时任务
    """
    # 采集数据
    session = db.session
    task_obj = None

    print("task running begin ....   target: %s   type(target): %s" % (target, type(target)))
    if target:
        session.query(PeriodTask).filter(PeriodTask.id == target).update({PeriodTask.status: 'running',
                                                                          PeriodTask.detail: ''
                                                                          })
        session.commit()

        task_obj = session.query(PeriodTask).filter(PeriodTask.id == target).first()
        print("task running ....  value: %s" % task_obj)
    if task_obj:

        # 添加任务记录
        record = TaskRecord(task_id=task_obj.id, task_name=task_obj.name)

        try:
            CollectInter.collect_tb_data(task_obj.id, task_obj.name, task_obj.collect_rule)
            # 校验数据
            if task_obj.validate_rule_id:
                validate_rule = task_obj.validate_rule
                types = validate_rule.types
                type_names = [item.name for item in types]
                for name in type_names:
                    getattr(ValidateInter, name)(validate_rule)
        except Exception as exc:
            print("task error: %s " % str(exc))
            session.query(PeriodTask).filter(PeriodTask.id == target).update({PeriodTask.status: 'failed',
                                                                              PeriodTask.detail: str(exc)
                                                                              })
            record.is_success = False
            record.reason = str(exc)
        else:
            print("task running success ....  value: %s" % task_obj)
            session.query(PeriodTask).filter(PeriodTask.id == target).update({PeriodTask.status: 'success',
                                                                              PeriodTask.detail: ''
                                                                              })
            record.is_success = True
            record.reason = ''

        session.add(record)
        session.commit()


def get_tasks():
    task_infos = []
    tasks = db.session.query(PeriodTask).all()
    for item in tasks:
        interval = item.interval.split()
        scheduler = crontab(minute=interval[0], hour=interval[1], day_of_month=interval[2], month_of_year=interval[3],
                            day_of_week=interval[4])
        task_infos.append((scheduler, item.id))
    return task_infos


tasks_info = get_tasks()

for key, value in tasks_info:
    celery_app.add_periodic_task(key, generate_task.s(value))
