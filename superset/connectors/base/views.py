# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from superset.exceptions import SupersetException
from superset.views.base import SupersetModelView


DELETE_ERROR_MSG = u"删除失败。请删除关联的报表：%s "


class DatasourceModelView(SupersetModelView):
    def pre_delete(self, obj):
        if obj.slices:
            raise SupersetException(DELETE_ERROR_MSG % ' , '.join([o.slice_name for o in obj.slices]))
