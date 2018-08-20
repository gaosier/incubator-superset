# -*- coding:utf-8 -*-
# __author__ = majing
"""
具体采集，校验函数
"""
import json
import logging
import datetime

from odps.df import DataFrame
from odps.df.expr.groupby import GroupBy, CollectionExpr
from odps.df.backends.frame import ResultFrame

from sqlalchemy.orm import load_only

from .base import get_odps
from .collections.models import CollectRecord
from .validates.models import ValidateRecord
from superset.models.core_ext import MProject, MPage

odps_app = get_odps()


class GenRecord(object):

    _record_cls = {'CollectRecord': CollectRecord, "ValidateRecord": ValidateRecord}

    @classmethod
    def create_record(cls, cls_name, **kwargs):
        if cls_name in cls._record_cls:
            cls._record_cls.get(cls_name).add_task_record(**kwargs)


class AlarmInter(object):

    @classmethod
    def send_mail(cls, users):
        pass


class CollectInter(object):

    @classmethod
    def collect_tb_data(cls, rule):
        """
        数据采集
        """
        is_success = False
        df = reason = None
        try:
            partition = rule.partition
            logging.info("collect_tb_data: table_name: %s  pro_name:%s  partion: %s" % (rule.table_name, rule.pro_name,
                                                                                          partition))
            if partition:
                df = DataFrame(odps_app.get_table(rule.table_name, project=rule.pro_name).get_partition(partition))
            else:
                df = DataFrame(odps_app.get_table(rule.table_name, project=rule.pro_name))
            if not df:
                reason = u"获取到的数据为空: 分区： %s" % partition
            else:
                if rule.all_fields:
                    df = df[rule.all_fields]
                is_success = True
        except Exception as exc:
            reason = str(exc)

        return is_success, reason, df

    @classmethod
    def collect_db_data(cls):
        pass


class ValidateInter(object):

    @classmethod
    def __get_md_pds(cls, session):
        values = session.query(MProject).options(load_only("id")).distinct()
        logging.info("project id: %s" % values)
        return values

    @classmethod
    def __get_md_pads(cls, session):
        values = session.query(MPage).options(load_only("page_id")).distinct()
        logging.info("project page id: %s" % values)
        return values

    @classmethod
    def __get_pro_table_name(cls, pro_name, tb_name):
        return "%s.%s" % (pro_name, tb_name)

    @classmethod
    def __is_validate_error(cls, pro_name, table_name):
        """
        判断一个表是否配置了错误校验
        """
        pass

    @classmethod
    def __get_validate_error(cls, pro_name, table_name):
        """
        获取一个表的错误校验配置
        """
        pass

    @classmethod
    def repeat(cls, df, fields):
        """
        重复数据校验
        """
        is_repeat = False
        detail_info = None
        logging.info("repeat fields: %s " % fields)

        result = df.groupby(fields).agg(count=df.count()).sort('count', ascending=False).head(5)
        logging.info("repeat result: %s " % result)

        for item in result:
            values = item.tolist()
            if values[-1] > 1:
                is_repeat = True
            break

        if is_repeat:
            detail_info = result.to_html()

        return is_repeat, detail_info

    @classmethod
    def missing(cls, collect):
        """
        缺失数据
        """
        is_missing = False
        msg = ''

        partition = collect.partition
        fields = collect.missing_fields
        filters = ""
        for name in fields:
            filters += "(%s is NULL) or " % name
        filters = filters.lstrip()
        filters = filters[: -3]
        logging.info("missing: filter: %s" % filters)

        sql = "select count(*) from %s where %s and (%s) ;" % (cls.__get_pro_table_name(collect.pro_name,
                                                                                        collect.table_name),
                                                               partition, filters)
        logging.info("missing: sql: %s" % sql)

        instance = odps_app.execute_sql(sql)

        with instance.open_reader() as reader:
            for record in reader:
                values = record.values
                logging.info("missing: values: %s" % values)
                if values[0] > 0:
                    is_missing = True
                    msg = "%s has null value, total error number is %s. sql: %s" % (fields, values[0], sql)
        return is_missing, msg

    @classmethod
    def tb_count(cls, rule):
        """
        表数据量
        """
        print('table column count ...')

    @classmethod
    def db_count(cls, rule):
        """
        数据库中表的数量
        """
        print('database table count ....')

    @classmethod
    def error(cls, collect):
        """
        错误校验 
        """
        logging.info("error validate: pro_name: %s   table_name: %s" % (collect.pro_name, collect.table_name))
        if cls.__is_validate_error(collect.pro_name, collect.table_name):
            error_conf = cls.__get_validate_error(collect.pro_name, collect.table_name)
            try:
                conf = json.loads(error_conf.rule)
            except Exception as e:
                pass    ## 添加校验记录
            else:
                if isinstance(conf, dict):
                    for field, func in conf.items():
                        getattr(cls, func)(field)

    @classmethod
    def validate_user_id(cls, collect, length=10):
        """
        校验用户ID
        :return: 
        """
        is_error = False
        msg = ''

        partition = collect.partition

        sql = "select count(*) from %s where %s and (LENGTH(uid) > %s or uid rlike '[^0-9]*[0-9]+[^0-9]*') ;" % (cls.__get_pro_table_name(collect.pro_name,
                                                                                                    collect.table_name),
                                                                           partition, length)
        logging.info("validate_user_id: sql: %s" % sql)

        instance = odps_app.execute_sql(sql)

        with instance.open_reader() as reader:
            for record in reader:
                values = record.values
                if values[0] > 0:
                    is_error = True
                    msg = "[uid] of table %s has error value, total error number %s. sql: %s" % (collect.table_name,
                                                                                                values[0], sql)
        return is_error, msg

    @classmethod
    def validate_pro_id(cls, collect, session):
        """
        校验项目ID
        :return: 
        """
        is_error = False
        msg = ''
        pds = cls.__get_md_pds(session)

        partition = collect.partition
        sql = "select count(*) from %s where %s and pd not in %s ;" % (cls.__get_pro_table_name(collect.pro_name,
                                                                                              collect.table_name
                                               ), partition, pds)
        logging.info("validate_pro_id: sql: %s" % sql)

        instance = odps_app.execute_sql(sql)

        with instance.open_reader() as reader:
            for record in reader:
                values = record.values
                if values[0] > 0:
                    is_error = True
                    msg = "[pd] of table %s has error value, total error number %s. sql: %s" % (collect.table_name,
                                                                                                 values[0], sql)
        return is_error, msg

    @classmethod
    def validate_page_id(cls, collect, session):
        """
        校验页面ID
        :return: 
        """
        is_error = False
        msg = ''
        pads = cls.__get_md_pads(session)

        partition = collect.partition
        sql = "select count(*) from %s where %s and pad not in %s ;" % (cls.__get_pro_table_name(collect.pro_name,
                                                                                                collect.table_name
                                                                                                ), partition, pads)
        logging.info("validate_page_id: sql: %s" % sql)

        instance = odps_app.execute_sql(sql)

        with instance.open_reader() as reader:
            for record in reader:
                values = record.values
                if values[0] > 0:
                    is_error = True
                    msg = "[pd] of table %s has error value, total error number %s. sql: %s" % (collect.table_name,
                                                                                                values[0], sql)
        return is_error, msg

    @classmethod
    def validate_time(cls, collect):
        """
        校验时间戳
        :return: 
        """
        is_error = False
        msg = ''

        partition = collect.partition
        min_time = '1970-01-01 00:00:00'
        max_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sql = "select count(*) from %s where %s and (from_unixtime(st/1000) < %s or from_unixtime(st/1000) > %s );" % \
              (cls.__get_pro_table_name(collect.pro_name,collect.table_name), partition, min_time, max_time)
        logging.info("validate_page_id: sql: %s" % sql)

        instance = odps_app.execute_sql(sql)

        with instance.open_reader() as reader:
            for record in reader:
                values = record.values
                if values[0]:
                    is_error = True
                    msg = "[st] of table %s has error value, total error number %s. sql: %s" % (collect.table_name,
                                                                                                values[0], sql)
        return is_error, msg

    @classmethod
    def logic_validate(cls):
        """
        逻辑校验
        :return: 
        """
        pass