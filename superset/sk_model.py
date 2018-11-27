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

        self.time_shift = timedelta()

        self.status = None
        self.error_message = None
        self.force = force

    def get_fillna_for_col(self, col):
        """Returns the value for use as filler for a specific Column.type"""
        if col:
            if col.is_string:
                return ' NULL'
        return self.default_fillna

    def get_fillna_for_columns(self, columns=None):
        """Returns a dict or scalar that can be passed to DataFrame.fillna"""
        if columns is None:
            return self.default_fillna
        columns_dict = {col.column_name: col for col in self.datasource.columns}
        fillna = {
            c: self.get_fillna_for_col(columns_dict.get(c))
            for c in columns
        }
        return fillna

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
            fillna = self.get_fillna_for_columns(df.columns)
            df = df.fillna(fillna)
        return df

    def get_json(self):
        return json.dumps(
            self.get_payload(),
            default=utils.json_int_dttm_ser, ignore_nan=True)

    def get_payload(self, query_obj=None):
        """Returns a payload of metadata and data"""
        payload = self.get_df_payload(query_obj)

        df = payload.get('df')
        if self.status != utils.QueryStatus.FAILED:
            if df is not None and df.empty:
                payload['error'] = 'No data'
            else:
                payload['data'] = self.get_data(df)
        if 'df' in payload:
            del payload['df']
        return payload

    def get_df_payload(self, query_obj=None):
        """Handles caching around the df payload retrieval"""
        stacktrace = None
        df = None

        try:
            df = self.get_df(query_obj)
            if self.status != utils.QueryStatus.FAILED:
                stats_logger.incr('loaded_from_source')
        except Exception as e:
            logging.exception(e)
            if not self.error_message:
                self.error_message = escape('{}'.format(e))
            self.status = utils.QueryStatus.FAILED
            stacktrace = traceback.format_exc()

        return {
            'df': df,
            'error': self.error_message,
            'form_data': self.form_data,
            'query': self.query,
            'status': self.status,
            'stacktrace': stacktrace,
            'rowcount': len(df.index) if df is not None else 0,
        }

    def json_dumps(self, obj, sort_keys=False):
        return json.dumps(
            obj,
            default=utils.json_int_dttm_ser,
            ignore_nan=True,
            sort_keys=sort_keys,
        )

    @property
    def data(self):
        """This is the data object serialized to the js layer"""
        content = {
            'form_data': self.form_data,
            'token': self.token,
            'viz_name': self.sk_type,
            'filter_select_enabled': self.datasource.filter_select_enabled,
        }
        return content

    def get_data(self, df):
        return []

    @property
    def json_data(self):
        return json.dumps(self.data)
