# -*- coding:utf-8 -*-
# __author__ = majing

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from collections import defaultdict
import copy
from datetime import datetime, timedelta
import hashlib
import inspect
from itertools import product
import logging
import math
import traceback
import uuid

from dateutil import relativedelta as rdelta
from flask import escape, request
from flask_babel import lazy_gettext as _
import geohash
from geopy.point import Point
from markdown import markdown
import numpy as np
import pandas as pd
from pandas.tseries.frequencies import to_offset
from pandas import Index
from pandas.core.indexes.multi import MultiIndex
import polyline
import simplejson as json
from six import string_types, text_type
from six.moves import cPickle as pkl, reduce

from superset import app, cache, get_manifest_file, utils, conf
from superset.utils import DTTM_ALIAS, JS_MAX_INTEGER, merge_extra_filters
from superset.exceptions import SupersetParamException


config = app.config
stats_logger = config.get('STATS_LOGGER')

METRIC_KEYS = [
    'metric', 'metrics', 'percent_metrics', 'metric_2', 'secondary_metric',
    'x', 'y', 'size',
]


BASE_QUERY = "SELECT * FROM  "


class BaseSkModel(object):
    """
    机器学习模型的基类
    """

    sk_type = None
    verbose_name = 'Base SK Model'
    credits = ''
    is_timeseries = False
    default_fillna = 0
    cache_type = 'df'

    def __init__(self, datasource, form_data, force=False):
        if not datasource:
            raise Exception("缺少数据源")
        self.datasource = datasource
        self.request = request
        self.sk_type = form_data.get("sk_type")
        self.form_data = form_data

        self.query = BASE_QUERY + self.datasource.table_name + ';'
        self.token = self.form_data.get(
            'token', 'token_' + uuid.uuid4().hex[:8])

        self.status = None
        self.error_message = None
        self.force = force

    def get_df(self, query_obj=None):
        """
         Returns a pandas dataframe based on the query object
        """
        self.error_msg = ''
        self.results = None

        self.results = self.datasource.query(query_obj, special_sql=self.query)
        self.query = self.results.query
        self.status = self.results.status
        self.error_message = self.results.error_message

        df = self.results.df
        if df is None or df.empty:
            return pd.DataFrame()
        else:
            df.replace([np.inf, -np.inf], np.nan)
        return df

    def get_column_fillna(self, df, fills):
        """
        获取每一列需要填充的值
        """
        fillna = {}
        for field, na in fills:
            if na == 'median':     # 中位数
                value = df[field].median()

            elif na == 'mode':    # 众数
                 mode = df[field].mode().tolist()
                 value = mode[0]

            elif na == 'mean':   # 平均值
                value = df[field].mean()

            else:
                value = na
            fillna[field] = value
        return fillna

    def deal_na(self, df):
        """
        缺失值处理
        """
        operate_info = self.form_data.get("null_operate")
        operate = operate_info.get("operate")
        if not operate:
            raise SupersetParamException(u"参数[operate]不能为空")
        detail = operate_info.get("detail")
        fillna = self.get_column_fillna(df, detail)

        if operate == "fill":
            df = df.fillna(fillna)
        else:
            df = df.dropna()
        return df

    def deal_variable_box(self, df):
        """
        变量分箱处理
        """
        variable_box = self.form_data.get("variable_box")
        for item in variable_box:
            field = item.get("field")
            bins = item.get("bins")
            labels = item.get("labels")
            if not field or (not bins) or (not labels):
                return df
            col = pd.cut(df[field], bins=bins, labels=labels)
            df[field] = col
        return df

    def deal_dummy_variable(self, df):
        """
        哑变量处理
        """
        dummy_variable = self.form_data.get("dummy_variable")
        for field, value in dummy_variable.items():
            df[field] = df[field].map(value)
        return df

    def variable_describe(self, df):
        """
        变量分布
        """
        data = df.describe()
        return data.to_html()







class Lasso(BaseSkModel):
    sk_type = 'lasso'


sk_types = {
    o.sk_type: o for o in globals().values()
    if (
        inspect.isclass(o) and
        issubclass(o, BaseSkModel) and
        o.sk_type not in config.get('VIZ_TYPE_BLACKLIST'))}
