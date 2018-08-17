# -*- coding:utf-8 -*-
# __author__ = majing
import json
from superset import celery_app, db
from celery.schedules import crontab
from celery_once import QueueOnce

from ..funcs import CollectInter, ValidateInter, GenRecord


from .models import PeriodTask, TaskRecord, CeleryRestartRecord
from ..utils import get_celery_beat_worker_pid


@celery_app.task(base=QueueOnce, once={'graceful': True}, ignore_result=True)
def generate_task(task_id):
    """
    生成定时任务
    """
    print("task running begin ....   target: %s   type(target): %s" % (task_id, type(task_id)))
    session = db.create_scoped_session()
    # 添加任务记录
    record = TaskRecord(is_success=True, reason='')
    try:
        PeriodTask.update_task_status_by_id(task_id, session=session)      # 设置task的状态为running

        task_obj = PeriodTask.get_task_by_id(task_id, session=session)
        print("task running ....  value: %s" % task_obj)
        collect_r = task_obj.collect_rule
        if collect_r:
            is_success, reason, df = CollectInter.collect_tb_data(collect_r)

            GenRecord.create_record('CollectRecord', task_id=task_id, task_name=task_obj.name, is_success=is_success,
                                    reason=reason, collect_rule_id=collect_r.id, collect_rule_name=collect_r.name,
                                    session=session)
            # 校验数据
            if task_obj.validate_rule_id and is_success:
                validate_rule = task_obj.validate_rule
                types = validate_rule.types
                type_names = [item.name for item in types]
                for _name in type_names:
                    getattr(ValidateInter, _name)(df, collect_r.repeat_fields)
        else:
            record.is_success = False
            record.reason = u"错误原因：采集规则为空"

        record.task_id = task_obj.id
        record.task_name = task_obj.name
    except Exception as exc:
        print("task error: %s " % str(exc))

        task_status = 'failed'
        error_msg = str(exc)

        record.task_id = -1
        record.task_name = 'NULL'
        record.is_success = False
        record.reason = str(exc)
    else:
        print("task running success ....  value: %s" % task_obj)

        task_status = 'success' if record.is_success else 'failed'
        error_msg = '' if record.is_success else record.reason

    PeriodTask.update_task_status_by_id(task_id, task_status, error_msg, session=session)  # 设置task的状态

    TaskRecord.create_record_by_obj(record, session=session)    # 创建任务记录

    session.commit()
    session.close()


@celery_app.task(base=QueueOnce, once={'graceful': True}, ignore_result=True)
def get_new_celery_pids():
    new_pids = get_celery_beat_worker_pid()
    print("get_new_celery_pids:  new_pids: ", new_pids)
    if new_pids:
        session = db.create_scoped_session()
        records = session.query(CeleryRestartRecord).filter(CeleryRestartRecord.status == 'running').all()
        for record in records:
            is_restart = 'success'
            msg = ''
            try:
                old_pids = json.loads(record.old_pids)
                print("get_new_celery_pids: old_pids:  ", old_pids)
                for key, value in old_pids.items():
                    if value == new_pids.get(key):
                        msg = '%s is restart falied' % key
                        is_restart = 'falied'
                        break
            except Exception as exc:
                msg = str(exc)

            record.cur_pids = new_pids
            record.reason = msg
            record.is_restart = is_restart
            record.status = 'complete'

            session.commit()
        session.close()


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

scheduler = crontab(minute='*/5', hour='*', day_of_month='*', month_of_year='*', day_of_week='*')
celery_app.add_periodic_task(scheduler, get_new_celery_pids.s())
