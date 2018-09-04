# -*- coding:utf-8 -*-
# __author__ = majing

import json

from superset.monitor.base import get_odps

from .sync_king import SupersetMemcached
from .validate_funcs_base import ValidateInter

odps_app = get_odps()


class ValidateOtherInter(ValidateInter):

    @classmethod
    def sync_king_minute(cls, validate, session=None, **kwargs):
        is_error = False
        msg = '金刚缓存每5分钟同步成功'
        try:
            superset = SupersetMemcached(table_conf=json.loads(validate.fields), session=session)
            error_add_tabs, error_add_columns = superset.set_minute()
            if error_add_tabs or error_add_columns:
                is_error = True
                msg = "添加失败的表: %s\n   添加失败的列: %s" % (error_add_tabs, error_add_columns)

        except Exception as exc:
            is_error = True
            msg = u"金刚缓存同步失败：%s" % str(exc)

        return is_error, msg

    @classmethod
    def sync_king_day(cls, validate, session=None, **kwargs):
        try:
            superset = SupersetMemcached(table_conf=json.loads(validate.fields), session=session)
            error_update_info = superset.set_day()
            if error_update_info:
                is_error = True
                msg = u"执行失败：更新失败的表和字段信息： %s" % error_update_info
            else:
                is_error = False
                msg = u"金刚缓存每天同步成功"
        except Exception as exc:
            is_error = True
            msg = u"金刚缓存每天同步失败：%s" % str(exc)
        return is_error, msg