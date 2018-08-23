# -*- coding:utf-8 -*-
# __author__ = majing
import json
import logging
import datetime

from superset import celery_app, db
from celery.schedules import crontab
from celery_once import QueueOnce

from ..funcs import CollectInter, ValidateInter, GenRecord, AlarmInter


from .models import PeriodTask, TaskRecord, CeleryRestartRecord
from ..utils import get_celery_beat_worker_pid


@celery_app.task(base=QueueOnce, once={'graceful': True}, ignore_result=True)
def generate_task(task_id):
    """
    生成定时任务
    """
    session = db.create_scoped_session()

    task_obj = PeriodTask.get_task_by_id(task_id, session=session)
    logging.info("task running ....  value: %s" % task_obj)

    # 添加任务记录
    is_success = True
    reason = ''
    task_record_id = TaskRecord.add_task_record(task_id=task_obj.id, task_name=task_obj.name, is_success=is_success,
                                           created_on=datetime.datetime.now(), session=session)
    validate_record_ids = []
    try:
        PeriodTask.update_task_status_by_id(task_id, session=session)      # 设置task的状态为running
        collect_r = task_obj.collect_rule
        if collect_r:
            # 校验数据
            if task_obj.validate_rule_id:
                validate_rule = task_obj.validate_rule
                types = validate_rule.types
                type_names = [item.name for item in types]
                for name in type_names:
                    is_repeat, detail = getattr(ValidateInter, name)(collect_r, session=session)
                    logging.info("operation: %s   result: %s    detail: %s" % (name, is_repeat, detail))
                    record_id = GenRecord.create_record('ValidateRecord', task_id=task_id, task_name=task_obj.name,
                                            is_success=is_repeat, operation=name,
                            reason=detail, validate_rule_id=validate_rule.id, validate_rule_name=validate_rule.name,
                            session=session)
                    if is_repeat and record_id:
                        validate_record_ids.append(record_id)
        else:
            is_success = False
            reason = u"错误原因：采集规则为空"
    except Exception as exc:
        logging.error("task error: %s " % str(exc))

        task_status = 'failed'
        error_msg = str(exc)

        is_success = False
        reason = str(exc)
    else:
        logging.info("task running success ....  value: %s" % task_obj)

        task_status = 'success' if is_success else 'failed'
        error_msg = '' if is_success else reason

    PeriodTask.update_task_status_by_id(task_id, task_status, error_msg, session=session)  # 设置task的状态

    TaskRecord.update_record_by_id(task_record_id, is_success=is_success, detail=reason, session=session)    # 创建任务记录

    if task_obj.alarm_rule:
        if validate_record_ids:
            is_email, msg_ = AlarmInter.alarm(task_obj.alarm_rule, task_obj.name, task_record_id, validate_record_ids,
                                              session)

            GenRecord.create_record('AlarmRecord', task_id=task_id, task_name=task_obj.name,
                                    is_success=is_email, reason=msg_, alarm_id=task_obj.alarm_rule.id,
                                    alarm_name=task_obj.alarm_rule.name,
                                    session=session)

    session.commit()
    session.close()


@celery_app.task(base=QueueOnce, once={'graceful': True}, ignore_result=True)
def get_new_celery_pids():
    new_pids = get_celery_beat_worker_pid()
    logging.info("get_new_celery_pids:  new_pids: ", new_pids)
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
    tasks = db.session.query(PeriodTask).filter(PeriodTask.is_active == 1).all()
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
