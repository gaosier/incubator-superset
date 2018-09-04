# -*- coding:utf-8 -*-
# __author__ = majing

from superset.monitor.base import get_odps

from .validate_funcs_base import ValidateInter

odps_app = get_odps()


class ValidateSqlInter(ValidateInter):

    @classmethod
    def execute_sql(cls, validate, **kwargs):
        is_error, msg = (False, '[%s]没有错误值' % validate.name)

        if validate.sql_expression:
            value = cls.get_sql_result(validate.sql_expression)
            if validate.min_compare_v:
                if value < validate.min_compare_v:
                    is_error = True
                    msg = '[%s]<FONT color= #FF0000>有错误值' % validate.name

                    return is_error, msg

            if validate.max_compare_v:
                if value > validate.max_compare_v:
                    is_error = True
                    msg = '[%s]有错误值' % validate.name

        return is_error, msg