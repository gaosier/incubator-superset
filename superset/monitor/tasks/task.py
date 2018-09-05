# -*- coding:utf-8 -*-
# __author__ = majing
import datetime
import json

from celery.schedules import crontab
from celery_once import QueueOnce

from superset import celery_app, db
from superset.monitor.interface import GenRecord, AlarmInter, ValidateEmailInter, ValidateFuncInter, ValidateSqlInter, \
    ValidateOtherInter
from .models import PeriodTask, TaskRecord, CeleryRestartRecord
from ..utils import get_celery_beat_worker_pid, logger


VALIDATE_TYPE_MAP = {"func": ValidateFuncInter, "email": ValidateEmailInter, "sql": ValidateSqlInter,
                     "other": ValidateOtherInter}


def get_validate_error_records(task_obj, session):
    error_validate_record_ids = []
    validate_rule = task_obj.validate_rule
    funcs = validate_rule.funcs
    func_names = [item.name for item in funcs]
    cls = VALIDATE_TYPE_MAP.get(validate_rule.classify_name)
    for name in func_names:
        is_repeat, detail = getattr(cls, name)(task_obj.validate_rule, session=session)
        logger.info("operation: %s   result: %s    detail: %s" % (name, is_repeat, detail))
        record_id = GenRecord.create_record('ValidateRecord', task_id=task_obj.id, task_name=task_obj.name,
                                            is_success=is_repeat, operation=name,
                                            reason=detail, validate_rule_id=validate_rule.id,
                                            validate_rule_name=validate_rule.name,
                                            session=session)

        if is_repeat and record_id:
            error_validate_record_ids.append(record_id)
    return error_validate_record_ids


def get_email_info(task_obj, session):
    email_infos = []
    alarm_rule = task_obj.alarm_rule
    validate_rule = task_obj.validate_rule
    funcs = validate_rule.funcs
    func_names = [item.name for item in funcs]
    cls = VALIDATE_TYPE_MAP.get(validate_rule.classify_name)
    user_ids = [user.id for user in alarm_rule.user]
    for name in func_names:
        is_success, detail, table_html = getattr(cls, name)(user_ids=user_ids)
        logger.info("operation: %s   result: %s    detail: %s" % (name, is_success, detail))
        GenRecord.create_record('ValidateRecord', task_id=task_obj.id, task_name=task_obj.name,
                                            is_success=is_success, operation=name,
                                            reason=detail, validate_rule_id=validate_rule.id,
                                            validate_rule_name=validate_rule.name,
                                            session=session)
        email_infos.append(table_html)

    return email_infos


@celery_app.task(base=QueueOnce, once={'graceful': True}, ignore_result=True)
def generate_task(task_id):
    """
    生成定时任务
    """
    session = db.create_scoped_session()

    task_obj = PeriodTask.get_task_by_id(task_id, session=session)
    logger.info("task running ....  value: %s" % task_obj)

    # 添加任务记录
    is_success = True
    reason = ''
    task_record_id = TaskRecord.add_task_record(task_id=task_obj.id, task_name=task_obj.name, is_success=is_success,
                                                created_by_fk=task_obj.created_by_fk, session=session)
    validate_record_ids = []
    try:
        PeriodTask.update_task_status_by_id(task_id, session=session)      # 设置task的状态为running
        # 校验数据
        if task_obj.validate_rule_id:
            validate_record_ids = get_validate_error_records(task_obj, session)
        else:
            is_success = False
            reason = u"错误原因：校验规则为空"
    except Exception as exc:
        logger.error("task error: %s " % str(exc))

        task_status = 'failed'
        error_msg = str(exc)

        is_success = False
        reason = str(exc)
    else:
        logger.info("task running success ....  value: %s" % task_obj)

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
                                    alarm_name=task_obj.alarm_rule.name, created_by_fk=task_obj.created_by_fk,
                                    session=session)

    session.commit()
    session.close()


@celery_app.task(base=QueueOnce, once={'graceful': True}, ignore_result=True)
def get_new_celery_pids():
    new_pids = get_celery_beat_worker_pid()
    logger.info("get_new_celery_pids:  new_pids: ", new_pids)
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


@celery_app.task(base=QueueOnce, once={'graceful': True}, ignore_result=True)
def generate_special_task(task_id):
    """
    生成定时任务
    """
    session = db.create_scoped_session()

    task_obj = PeriodTask.get_task_by_id(task_id, session=session)
    logger.info("generate_special_task running ....  value: %s" % task_obj)

    # 添加任务记录
    is_success = True
    reason = ''
    task_record_id = TaskRecord.add_task_record(task_id=task_obj.id, task_name=task_obj.name, is_success=is_success,
                                                created_by_fk=task_obj.created_by_fk, session=session)
    table_htmls = []
    try:
        PeriodTask.update_task_status_by_id(task_id, session=session)      # 设置task的状态为running
        # 校验数据
        if task_obj.validate_rule_id:
            table_htmls = get_email_info(task_obj, session)
            logger.info("table_htmls: %s" % table_htmls)
        else:
            is_success = False
            reason = u"错误原因：校验规则为空"
    except Exception as exc:
        logger.error("generate_special_task error: %s " % str(exc))

        task_status = 'failed'
        error_msg = str(exc)

        is_success = False
        reason = str(exc)
    else:
        logger.info("generate_special_task running success ....  value: %s" % task_obj)

        task_status = 'success' if is_success else 'failed'
        error_msg = '' if is_success else reason

    PeriodTask.update_task_status_by_id(task_id, task_status, error_msg, session=session)  # 设置task的状态

    TaskRecord.update_record_by_id(task_record_id, is_success=is_success, detail=reason, session=session)    # 创建任务记录

    if task_obj.alarm_rule:
        if table_htmls:
            is_email, msg_ = AlarmInter.alarm_table_html(task_obj.alarm_rule, table_htmls, session=session)

            GenRecord.create_record('AlarmRecord', task_id=task_id, task_name=task_obj.name,
                                    is_success=is_email, reason=msg_, alarm_id=task_obj.alarm_rule.id,
                                    alarm_name=task_obj.alarm_rule.name, created_by_fk=task_obj.created_by_fk,
                                    session=session)

    session.commit()
    session.close()


def get_tasks():
    task_infos, special_tasks = [], []
    tasks = db.session.query(PeriodTask).filter(PeriodTask.is_active == 1).all()
    for item in tasks:
        interval = item.interval.split()
        scheduler = crontab(minute=interval[0], hour=interval[1], day_of_month=interval[2], month_of_year=interval[3],
                            day_of_week=interval[4])
        if item.validate_rule.is_email_classify:
            special_tasks.append((scheduler, item.id, item.name))
            continue

        task_infos.append((scheduler, item.id, item.name))
    return task_infos, special_tasks


tasks_info, special_tasks = get_tasks()

for key, value, name in tasks_info:
    celery_app.add_periodic_task(key, generate_task.s(value), name=name)

for key, value, name in special_tasks:
    celery_app.add_periodic_task(key, generate_special_task.s(value), name=name)

scheduler = crontab(minute='*/5', hour='*', day_of_month='*', month_of_year='*', day_of_week='*')
celery_app.add_periodic_task(scheduler, get_new_celery_pids.s())
