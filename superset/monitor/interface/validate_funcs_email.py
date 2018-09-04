# -*- coding:utf-8 -*-
# __author__ = majing
import datetime
import pandas as pd
import numpy as np

from .validate_funcs_base import ValidateInter
from superset.monitor.base import get_engine
from superset.monitor.utils import logger

engine = get_engine()


class ValidateEmailInter(ValidateInter):
    @staticmethod
    def format_col(val):
        if val >= 1:
            return "是"
        return "否"

    @classmethod
    def get_all_task_details(cls, **kwargs):
        table_htmls, msg, is_success = ({}, '', True)
        now = datetime.datetime.now()
        start_time = datetime.datetime(year=now.year, day=now.day, month=now.month).strftime('%Y-%m-%d')
        fields = ['task_name', 'validate_rule_name', 'operation', 'is_success']
        table_name = 'validate_record'
        try:
            sql = "select %s from %s where changed_on>='%s'" % (','.join(fields), table_name, start_time)
            df = pd.read_sql_query(sql, con=engine)
            df = df.pivot_table(df, index=['task_name', 'validate_rule_name', 'operation'], aggfunc=np.sum)
            logger.info("df: %s" % df)
            df['is_success'] = df['is_success'].map(cls.format_col)
            logger.info("df.index: %s" % df.index)
            logger.info("df.columns: %s" % df.columns)
        except Exception as exc:
            is_success = False
            msg = "失败原因: %s" % str(exc)
        else:
            table_html = df.to_html()
            table_htmls['all'] = table_html
            msg = u"获取所有的定时任务详情成功"
        return is_success, msg, table_htmls

    @classmethod
    def get_task_details_by_user(cls, user_ids=None, **kwargs):
        table_htmls, msg, is_success = ({}, '', True)
        now = datetime.datetime.now()
        start_time = datetime.datetime(year=now.year, day=now.day, month=now.month).strftime('%Y-%m-%d')
        fields = ['task_name', 'validate_rule_name', 'operation', 'is_success']
        table_name = 'validate_record'

        if user_ids:
            for user_id in user_ids:
                try:
                    sql = "select %s from %s where changed_on>='%s' and created_by_fk=%s" % (','.join(fields),
                                                                                             table_name, start_time,
                                                                                             user_id)
                    df = pd.read_sql_query(sql, con=engine)
                    df = df.pivot_table(df, index=['task_name', 'validate_rule_name', 'operation'], aggfunc=np.sum)
                    logger.info("df: %s" % df)
                except Exception as exc:
                    is_success = False
                    msg = "失败原因: %s" % str(exc)
                else:
                    table_html = df.to_html()
                    msg = u"获取所有的定时任务详情成功"
                    table_htmls[user_id] = table_html
        return is_success, msg, table_htmls
