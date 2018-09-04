# -*- coding:utf-8 -*-
# __author__ = majing
from odps.errors import ETParseError

from superset.monitor.validates.models import ValidateErrorRule
from superset.models.core_ext import MProject, MPage
from superset.monitor.utils import logger
from superset.monitor.base import get_odps

odps_app = get_odps()


class ValidateInter(object):

    @classmethod
    def __get_md_pds(cls, session):
        querys = session.query(MProject).all()
        values = [query.id for query in querys]
        logger.info("project id:  count:%s       values:%s" % (len(values), values))
        return tuple(values)

    @classmethod
    def __get_md_pads(cls, session):
        querys = session.query(MPage).all()
        values = [query.page_id for query in querys]
        logger.info("project page id: count:%s   values:%s" % (len(values), values))
        return tuple(values)

    @classmethod
    def __get_pro_table_name(cls, pro_name, tb_name):
        return "%s.%s" % (pro_name, tb_name)

    @classmethod
    def __get_validate_error(cls, pro_name, tab_name, session):
        """
        获取一个表的错误校验配置
        """
        return ValidateErrorRule.get_table_error_conf(pro_name, tab_name, session)

    @classmethod
    def gen_result_and_message(cls, error_pt, opation='repeat', pro_tab_name=None, fields=None, partitions=None):
        is_has_error = False

        if opation == "repeat":
            key = u"重复值"
        elif opation == "missing":
            key = u"缺失值"

        if not error_pt:
            error_msg = u"表[%s]的字段[%s]<span style='color:green'>没有%s</span>.分区: %s " % (pro_tab_name, fields, key, partitions)
        else:
            is_has_error = True
            error_msg = u"表[%s]的字段[%s]在分区%s<span style='color:red'>有%s</span>. " % (pro_tab_name, fields, partitions, key)
        return is_has_error, error_msg

    @classmethod
    def get_func_result(cls, sql):
        """
        获取校验函数中的sql的执行结果，调用此函数的校验函数属于func类型
        """
        is_error = False
        logger.info("get_func_result: %s" % sql)
        try:
            instance = odps_app.execute_sql(sql)

            with instance.open_reader() as reader:
                for record in reader:
                    values = record.values
                    logger.info("get_func_result values: %s" % values)
                    if values[0] > 1:
                        is_error = True
                    break
        except (ETParseError, Exception) as exc:
            raise ValueError("get_func_result error: %s" % str(exc))

        return is_error

    @classmethod
    def get_sql_result(cls, sql):
        """
        获取校验函数的sql的执行结果，调用此函数的校验函数属于sql类型
        """
        value = 0
        logger.info("get_sql_result: sql: %s" % sql)
        try:
            instance = odps_app.execute_sql(sql)

            with instance.open_reader() as reader:
                for record in reader:
                    values = record.values
                    logger.info("get_sql_result: %s" % values)
                    if values[0]:
                        value = values[0]
        except (ETParseError, Exception) as exc:
            raise ValueError(u"get_sql_result执行sql失败: %s" % str(exc))

        return value

    @classmethod
    def get_table_partition_count(cls, sql, name, partition):
        count = 0
        instance = odps_app.execute_sql(sql)

        with instance.open_reader() as reader:
            for record in reader:
                values = record.values
                logger.info("[%s] in [%s]  total count: %s" % (name, partition, values))
                count = values[0]
        return count