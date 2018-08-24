# -*- coding:utf-8 -*-
# __author__ = majing

import logging
from sqlalchemy import create_engine
import datetime
from pandas import DataFrame
import sys
import re
from collections import defaultdict

from superset.utils_ext import get_memcached_engine
from superset.connectors.sqla.models import TableColumn, SqlaTable
from superset.config_ext import SUPERSET_MEMCACHED

"""
金刚数据同步：
1. 每5分钟同步一次，添加新增需要缓存的表和字段
2. 每天同步一次，同步列的值，删除不需要缓存的表和字段
"""
SUPERSET_HYBRID_DATABASE_URI = 'mysql://aixuexi_bi:Aixuexi1243@pub-m-2zea282c9e5ebe44.petadata.rds.aliyuncs.com/bi?charset=utf8'

RE_DICT = {
    'dm_user_behavior_path_yyyymmdd': {'pad': '^\w+\d+$'}
}

hybrid_engine = None


def get_hybrid_engine():
    global hybrid_engine
    if not hybrid_engine:
        hybrid_engine = create_engine(SUPERSET_HYBRID_DATABASE_URI)
    return hybrid_engine


class SupersetMemcached(object):

    def __init__(self, table_conf=None, session=None):
        self.hybrid_engine = get_hybrid_engine()
        self.mc = get_memcached_engine(SUPERSET_MEMCACHED)
        self.session = session
        self.table_conf = table_conf

    def deal_li(self, li):
        a = [li]
        flag = True
        while flag:
            for i, j in enumerate(a):
                if sys.getsizeof(j) > 1000**2:
                    le=len(j)
                    a.extend([j[0:le//2], j[le//2:]])
                    a.pop(i)
                    break
            else:
                flag=False
        return a

    def re_value(self,tab,col,li):
        re_cols = RE_DICT.get(tab, None)
        if re_cols:
            pattern = re_cols.get(col)
            if pattern:
                val=[]
                for i in li:
                    if re.search(pattern, i):
                        val.append(i)
                return val
        return li

    def set(self, li, key):
        li = self.deal_li(li)
        num_li = []
        for i, j in enumerate(li):
            name = '%s-%s' % (key, i)
            res = self.mc.set(name, j)
            if not res:
                logging.error("set value error ===>name: %s  value: %s" % (name, j))
                continue
            num_li.append(i)
        return num_li

    def get_tab_dict(self):
        """
        获取需要进行缓存的表以及字段信息
        :return:
        """
        tab_dict = defaultdict(list)
        query = self.session.query(TableColumn.column_name, SqlaTable.table_name).join(SqlaTable,
               SqlaTable.id == TableColumn.table_id).filter(TableColumn.is_memcached == 1,
                                                             TableColumn.filterable == 1).all()
        for column_name, table_name in query:
            tab_dict[table_name].append(column_name)
        return tab_dict

    def set_tabs_cols_info(self, tab_dict):
        """
        缓存表以及字段的相关信息
        :param tab_dict:
        :return:
        """
        result = self.mc.set('superset_memcached_tabs', tab_dict)
        if not result:
            logging.error("set memcached [superset_memcached_tabs] error:  tables: %s" % (tab_dict))

    def generate_df(self,data,cols):
        df = DataFrame(data, columns=cols)
        df = df.fillna('superset_nan')
        return df

    def hybrid_memcached_increment(self, tab, cols, is_new=False):
        """
        有分区的表跑增量
        """
        error_info = []

        part_type = self.table_conf.get(tab).get('pt', 'day')
        d_fomat = self.table_conf.get(tab).get('fm', '%Y%m%d')
        end_time = datetime.datetime.strptime((datetime.datetime.now() - datetime.timedelta(days=1)).strftime(d_fomat), d_fomat)
        start_time = end_time - datetime.timedelta(days=15) if is_new else end_time

        while start_time <= end_time:
            filter_time = start_time.strftime(d_fomat)
            sql = 'select distinct %s from %s WHERE %s="%s"' % (','.join(cols), tab, part_type, filter_time)
            result = self.hybrid_engine.execute(sql)
            df = self.generate_df(result.fetchall(), cols)
            error_info.extend(self.set_table_columns_value(tab, cols, is_new, df))
            start_time = start_time + datetime.timedelta(days=1)

        return list(set(error_info))

    def hybrid_memcached_full_quantity(self, tab, cols, is_new=False):
        """
        分区是全量
        """
        sql = 'select distinct %s from %s' % (','.join(cols), tab)
        result = self.hybrid_engine.execute(sql)
        df = self.generate_df(result.fetchall(), cols)
        error_info = list(set(self.set_table_columns_value(tab, cols, is_new, df)))

        return error_info

    def set_table_columns_value(self, tab, cols, is_new, df):
        """
        将columns的值设置到memcached中
        """
        error_info = []
        cols = cols if cols else []
        for m in cols:
            key = 'superset-%s-%s' % (tab, m)
            a = list(set(df[m]))

            logging.info("key: %s  len(value):%s " % (key, len(a)))

            if 'superset_nan' in a:
                a.remove('superset_nan')
            a = self.re_value(tab, m, a)

            if is_new:
                res = self.mc.set(key, self.set(a, key))
                if not res:
                    error_info.append(m)
            else:
                old_num_list = self.mc.get(key)
                logging.info("key: %s  old_num_list: %s" % (key, old_num_list))
                li = []
                if old_num_list:
                    for i in old_num_list:
                        _key = '%s-%s' % (key, i)
                        old_values = self.mc.get(_key)
                        li.extend(old_values)
                li.extend(a)
                sub_res = self.set(list(set(li)), key)
                res = self.mc.set(key, sub_res)
                if not res:
                    logging.error("set value error: key: %s   values: %s" % (key, sub_res))
                    error_info.append(m)
        return error_info

    def set_value_to_memcached(self, tab_info, is_new=False):
        """
        向memcached中插入数据
        is_new: 是否是新增的表或者字段，如果是，则同步一个月的数据；否则只同步一天的数据 
        """
        error_info = {}
        for tab, cols in tab_info.items():
            if tab in self.table_conf:
                error_columns = self.hybrid_memcached_increment(tab, cols, is_new)
            else:
                error_columns = self.hybrid_memcached_full_quantity(tab, cols, is_new)
            if error_columns:
                error_info[tab] = error_columns
        return error_info

    def set_day(self):
        """
        每天执行一次，用于增加每个字段新增加的信息
        以及删除取消勾选的字段以及删除的表
        :return:
        """
        if not self.is_connected():
            raise ValueError("金刚缓存同步失败：连不上memached.memached只能在内网访问")

        tab_dict = self.get_tab_dict()
        memcached_tabs_cols_dict = self.mc.get('superset_memcached_tabs') or defaultdict(list)
        error_update_info = self.set_value_to_memcached(memcached_tabs_cols_dict)

        del_tab = set(memcached_tabs_cols_dict) - set(tab_dict)
        check_tab = set(tab_dict) & set(memcached_tabs_cols_dict)
        for tab in del_tab:
            keys = []
            for col in memcached_tabs_cols_dict[tab]:
                key = 'superset-%s-%s' % (tab, col)
                keys.append(key)
                res = self.mc.get(key)
                if res and isinstance(res, list):
                    for i in res:
                        keys.append('%s-%s' % (key, i))
            del memcached_tabs_cols_dict[tab]
            self.mc.delete_multi(keys)

        for tab in check_tab:
            old_cols = set(memcached_tabs_cols_dict[tab])
            new_cols = set(tab_dict[tab])
            del_cols = old_cols - new_cols
            keys = []
            for col in del_cols:
                key = 'superset-%s-%s' % (tab, col)
                keys.append(key)
                rest = self.mc.get(key)
                if rest and isinstance(rest, list):
                    for i in rest:
                        keys.append('%s-%s' % (key, i))

            memcached_tabs_cols_dict[tab] = list(old_cols-del_cols)
            self.mc.delete_multi(keys)

        self.set_tabs_cols_info(memcached_tabs_cols_dict)
        return error_update_info

    def set_minute(self):
        """
        每五分钟执行一次，用于缓存增加的字段以及增加的表
        :return:
        """
        if not self.is_connected():
            raise ValueError("金刚缓存同步失败：连不上memached.memached只能在内网访问")

        error_add_tbs = error_add_cols = None
        tab_dict = self.get_tab_dict()
        memcached_tabs_cols_dict = self.mc.get('superset_memcached_tabs')

        logging.info('tab_dict: %s' % tab_dict)
        logging.info('memcached_tabs_cols_dict: %s ' % memcached_tabs_cols_dict)

        if memcached_tabs_cols_dict is None:
            memcached_tabs_cols_dict = defaultdict(list)

        add_tab = set(tab_dict) - set(memcached_tabs_cols_dict)
        check_tab = set(tab_dict) & set(memcached_tabs_cols_dict)

        logging.info('set_minute:  add_table: %s   check_table: %s' % (add_tab, check_tab))

        # 添加新表
        add_tab_dict = {tab: tab_dict.get(tab) for tab in add_tab}
        logging.info('new add table infos: %s' % add_tab_dict)
        if add_tab_dict:
            error_add_tbs = self.set_value_to_memcached(add_tab_dict, is_new=True)
            if error_add_tbs:
                success_tab = self.get_add_success_tables(add_tab_dict, error_add_tbs)
                memcached_tabs_cols_dict.update(success_tab)
            else:
                memcached_tabs_cols_dict.update(add_tab_dict)

        # 修改表中的某些字段
        add_tab_cols_dict = {}
        for tab in check_tab:
            old_cols = set(memcached_tabs_cols_dict[tab])
            new_cols = set(tab_dict[tab])
            add_cols = new_cols - old_cols
            if add_cols:
                add_tab_cols_dict[tab] = list(add_cols)
                memcached_tabs_cols_dict[tab] = list(old_cols | add_cols)

        logging.info("new add columns: %s " % add_tab_cols_dict)

        if add_tab_cols_dict:
            error_add_cols = self.set_value_to_memcached(add_tab_cols_dict, is_new=True)
            if error_add_cols:
                success = self.get_add_success_tables(add_tab_cols_dict, error_add_cols)
                for tab, cols in success:
                    old_cols = set(memcached_tabs_cols_dict.get(tab))
                    new_cols = set(cols)
                    memcached_tabs_cols_dict[tab] = list(old_cols | new_cols)

        self.set_tabs_cols_info(memcached_tabs_cols_dict)

        return error_add_tbs, error_add_cols

    def get_add_success_tables(self, src, dist):
        new = {}
        for tab, cols in src.items():
            errors = dist.get(tab)
            new[tab] = list(set(cols) - set(errors))
        return new

    def is_connected(self):
        res = self.mc.set('test', '1111')
        if res:
            self.mc.delete('test')
            return True
        return False
