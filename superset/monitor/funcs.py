# -*- coding:utf-8 -*-
# __author__ = majing
"""
具体采集，校验函数
"""
import json
from pandas import DataFrame as PdDataFrame

from odps.df import DataFrame

from .base import get_odps
from .collections.models import CollectRecord, CollectRule

odps_app = get_odps()


class CollectInter(object):

    @classmethod
    def collect_tb_data(cls, task_id, task_name, rule):
        """
        数据采集
        """
        is_success = False
        df = reason = None
        try:
            if rule:
                partition = rule.partition
                if partition:
                    df = DataFrame(odps_app.get_table(rule.table_name, project=rule.pro_name).get_partition(partition))
                else:
                    df = DataFrame(odps_app.get_table(rule.table_name, project=rule.pro_name))
                if not df:
                    reason = u"获取到的数据为空: 分区： %s" % partition

                if rule.all_fields:
                    df = df[rule.all_fields]
                is_success = True
            else:
                reason = u"错误原因：采集规则为空"
        except Exception as exc:
            reason = str(exc)

        if rule:
            collect_rule_id = rule.id
            collect_rule_name = rule.name
        else:
            collect_rule_id = collect_rule_name = None

        CollectRecord.add_task_record(task_id=task_id, task_name=task_name, is_success=is_success, reason=reason,
                                      collect_rule_id=collect_rule_id, collect_rule_name=collect_rule_name)
        return df

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
    def repeat(cls, rule):
        """
        重复数据校验
        """
        print('validate repeat ...')
        # 采集记录
        # 如果失败, 告警

    @classmethod
    def missing(cls, rule):
        """
        缺失数据
        """
        print('validate missing ....')

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