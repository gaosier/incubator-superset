# -*- coding:utf-8 -*-
# __author__ = majing
import json
import datetime

from superset.monitor.utils import logger
from superset.monitor.base import get_odps

from .validate_funcs_base import ValidateInter

odps_app = get_odps()


class ValidateFuncInter(ValidateInter):

    @classmethod
    def repeat(cls, validate, **kwargs):
        """
        重复数据校验
        """
        error_pt = []
        partitions = validate.partition
        fields = validate.repeat_fields

        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)
        for pt in partitions:
            for item in fields:
                sql = "select count(*) as num from %s where %s GROUP BY %s HAVING num > 1 limit 1;" % (pro_tab_name, pt,
                                                                                                 ','.join(item))
                is_error = cls.get_func_result(sql)
                if is_error:
                    error_pt.append(pt)

        is_has_error, error_msg = cls.gen_result_and_message(error_pt, 'repeat', pro_tab_name, fields, partitions)
        return is_has_error, error_msg

    @classmethod
    def missing(cls, validate, **kwargs):
        """
        缺失数据
        """
        error_pt = []
        partitions = validate.partition
        fields = validate.missing_fields
        filters = ""
        for name in fields:
            filters += "(%s is NULL) or " % name
        filters = filters.lstrip()
        filters = filters[: -3]
        logger.info("missing: filter: %s" % filters)

        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)

        for pt in partitions:
            sql = "select count(*) from %s where %s and (%s) ;" % (pro_tab_name, pt, filters)
            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)

        is_has_error, error_msg = cls.gen_result_and_message(error_pt, 'missing', pro_tab_name, fields, partitions)

        return is_has_error, error_msg

    @classmethod
    def error(cls, validate, session=None):
        """
        错误校验 
        """
        key = "%s.%s" % (validate.pro_name, validate.tab_name)
        is_has_error = False
        error_msg = "表[%s]:\n" % key

        error_conf = cls.__get_validate_error(validate.pro_name, validate.tab_name, session)
        if error_conf:
            try:
                conf = json.loads(error_conf.rule)
            except Exception as e:
                error_msg = "[%s] error validate: error rule: %s     error msg: <span style='color:red'>%s</span>" % \
                            (key, error_conf.rule, str(e))
            else:
                logger.info("error conf: %s" % conf)
                for field, func in conf.items():
                    result = getattr(cls, func)(validate, field, session=session)
                    if result:
                        is_has_error = True
                        error_msg += "<span style='color:red'>字段[%s]在分区%s中有错误值</span>\n" % (field, result)
                    else:
                        error_msg += "<span style='color:green'>字段[%s]没有错误值</span>\n" % field

        else:
            error_msg = u"<span style='color:red'>表[%s]没有配置错误校验规则</span>." % key
        return is_has_error, error_msg

    @classmethod
    def validate_user_id(cls, validate, field, length=10, **kwargs):
        """
        校验用户ID
        """
        error_pt = []
        partitions = validate.partition
        logger.info("validate_user_id: partitions: %s" % partitions)
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name,validate.tab_name)

        for pt in partitions:
            sql = "select count(*) from %s where %s and (LENGTH(%s) > %s or %s rlike '([^0-9]+[0-9]+[^0-9]*)|([0-9]+[^0-9]+[^0-9]*)|([^0-9]*+[0-9]+[^0-9]+)') ;" % (
                pro_tab_name, pt, field, length, field)
            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)
        return error_pt

    @classmethod
    def validate_pro_id(cls, validate, field, session=None):
        """
        校验项目ID
        """
        error_pt = []

        pds = cls.__get_md_pds(session)
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)

        partitions = validate.partition
        logger.info("validate_pro_id: partitions: %s" % partitions)

        for pt in partitions:
            sql = "select count(*) from %s where %s and %s not in %s ;" % (pro_tab_name, pt, field, pds)
            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)
        return error_pt

    @classmethod
    def validate_page_id(cls, validate, field, session=None):
        """
        校验页面ID 
        """
        error_pt = []

        pads = cls.__get_md_pads(session)
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)
        partitions = validate.partition
        logger.info("validate_page_id: partitions: %s" % partitions)

        for pt in partitions:
            sql = "select count(*) from %s where %s and %s not in %s ;" % (pro_tab_name, pt, field, pads)
            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)
        return error_pt

    @classmethod
    def validate_time(cls, validate, field, **kwargs):
        """
        校验时间戳
        """
        error_pt = []

        partitions = validate.partition
        logger.info("validate_time: partitions: %s" % partitions)

        min_time = '1970-01-01 00:00:00'
        max_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name,validate.tab_name)

        for pt in partitions:
            sql = "select count(*) from %s where %s and (from_unixtime(%s/1000)<'%s' or from_unixtime(%s/1000)>'%s' );" % \
                  (pro_tab_name, pt, field, min_time, field, max_time)

            is_error = cls.get_func_result(sql)
            if is_error:
                error_pt.append(pt)
        return error_pt

    @classmethod
    def logic_validate(cls, validate, **kwargs):
        """
        逻辑校验
        """
        is_has_error = False
        error_msg = ''

        old_total_count, new_total_count = (0, 0)
        if validate.is_multi_days:
            end_time = validate.end_time
            start_time = validate.start_time
        else:
            end_time = datetime.datetime.now() - datetime.timedelta(days=1)
            start_time = datetime.datetime.now() - datetime.timedelta(days=1)
        do_start_time = start_time
        pro_tab_name = cls.__get_pro_table_name(validate.pro_name, validate.tab_name)
        table = odps_app.get_table(validate.tab_name, project=validate.pro_name)
        if 'dm' in table.name and table.schema.partitions:
            while do_start_time <= end_time:
                pt_end_time = (do_start_time - datetime.timedelta(days=2)).strftime("%Y%m%d")
                pt_start_time = (do_start_time - datetime.timedelta(days=8)).strftime("%Y%m%d")
                partition = "day>=%s and day<=%s" % (pt_start_time, pt_end_time)
                sql = "select count(*) from %s WHERE %s;" % (pro_tab_name, partition)
                old_total_count += cls.get_table_partition_count(sql, pro_tab_name, partition)

                new_date = (do_start_time - datetime.timedelta(days=1)).strftime("%Y%m%d")
                partition = "day=%s" % new_date
                sql = "select count(*) from %s WHERE %s;" % (pro_tab_name, partition)
                new_total_count += cls.get_table_partition_count(sql, pro_tab_name, partition)

                avg = old_total_count/7.0
                if int(avg * 0.5) <= new_total_count <= int(avg * 1.5):
                    do_start_time = do_start_time + datetime.timedelta(days=1)
                    continue

                is_has_error = True
                msg = "[分区]:%s   [表名]:%s  [7天平均值]:%s [当天数据量]:%s" % (pro_tab_name, partition, avg,
                                                                    new_total_count)
                error_msg += "%s\n" % msg
                do_start_time = do_start_time + datetime.timedelta(days=1)
        else:
            is_has_error = True
            error_msg = "只有集市表进行逻辑校验.表[%s]不是集市表或者表没有分区" % pro_tab_name

        if not is_has_error:
            error_msg = u"表[%s]在[%s ~ %s]没有错误值." % (pro_tab_name, start_time.strftime("%Y%m%d"),
                                                    end_time.strftime("%Y%m%d"))

        return is_has_error, error_msg