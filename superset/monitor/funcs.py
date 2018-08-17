# -*- coding:utf-8 -*-
# __author__ = majing
"""
具体采集，校验函数
"""
import json

from odps.df import DataFrame
from odps.df.expr.groupby import GroupBy

from .base import get_odps
from .collections.models import CollectRecord

odps_app = get_odps()


class GenRecord(object):

    _record_cls = {'CollectRecord': CollectRecord}

    @classmethod
    def create_record(cls, cls_name, **kwargs):
        if cls_name in cls._record_cls:
            cls._record_cls.get(cls_name).add_task_record(**kwargs)


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
            print("partion:  ", partition)
            if partition:
                df = DataFrame(odps_app.get_table(rule.table_name, project=rule.pro_name).get_partition(partition))
            else:
                df = DataFrame(odps_app.get_table(rule.table_name, project=rule.pro_name))
            if not df:
                reason = u"获取到的数据为空: 分区： %s" % partition
            else:
                # if rule.all_fields:
                #     df = df[rule.all_fields]
                is_success = True
        except Exception as exc:
            reason = str(exc)

        return is_success, reason, df

    @classmethod
    def collect_db_data(cls):
        pass


class ValidateInter(object):

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
        print("repeat ...... fields: ", fields)

        df_new = df.groupby(fields).count()
        print("df_new: group count: ", dir(df_new))

        print("df_new max:  ", df_new)
        print("repeat:   df having count", type(df_new))

        return is_repeat

    @classmethod
    def missing(cls, df, fields):
        """
        缺失数据
        """
        df = df[fields].isnull().any()
        print("missing:  df ", df)

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
    def error(cls, rule, pro_name=None, table_name=None):
        """
        错误校验 
        """
        print('validate data error .... ')
        if cls.__is_validate_error(pro_name, table_name):
            error_conf = cls.__get_validate_error(pro_name, table_name)
            try:
                conf = json.loads(error_conf.rule)
            except Exception as e:
                pass    ## 添加校验记录
            else:
                if isinstance(conf, dict):
                    for field, func in conf.items():
                        getattr(cls, func)(field)


    @classmethod
    def validate_user_id(cls):
        """
        校验用户ID
        :return: 
        """
        pass

    @classmethod
    def validate_pro_id(cls):
        """
        校验项目ID
        :return: 
        """
        pass

    @classmethod
    def validate_page_id(cls):
        """
        校验页面ID
        :return: 
        """
        pass

    @classmethod
    def validate_time(cls):
        """
        校验时间戳
        :return: 
        """
        pass

    @classmethod
    def logic_validate(cls):
        """
        逻辑校验
        :return: 
        """
        pass