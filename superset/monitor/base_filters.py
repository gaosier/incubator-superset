# -*- coding:utf-8 -*-
# __author__ = majing
"""
过滤函数
"""
from flask import g

from superset.views.base import SupersetFilter


class CommonFilter(SupersetFilter):
    def apply(self, query, func):
        if self.has_role('Admin'):
            return query
        return query.filter(self.model.created_by_fk == g.user.id)