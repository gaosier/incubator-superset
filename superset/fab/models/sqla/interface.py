#-*-coding:utf-8-*-
from sqlalchemy import func,distinct
from flask_appbuilder.models.sqla.interface import SQLAInterface as SAI

from . import filters
from superset.fab.models.filters import SupersetFilters


class SupersetSQLAInterface(SAI):

    filter_converter_class = filters.SuperSetSQLAFilterConverter

    def get_pk_column(self):
        pk_name = self.get_pk_name()
        pk_column = None
        for c in self.obj.__mapper__.columns:
            if pk_name == c.name:
                pk_column = c
                break
        return pk_column

    def query(self, filters=None, order_column='', order_direction='',
              page=None, page_size=None):
        """ 
            QUERY
            :param filters:
                dict with filters {<col_name>:<value,...}
            :param order_column:
                name of the column to order
            :param order_direction:
                the direction to order <'asc'|'desc'>
            :param page:
                the current page
            :param page_size:
                the current page size

        """
        query = self.session.query(self.obj)
        if len(order_column.split('.')) >= 2:
            tmp_order_column = ''
            for join_relation in order_column.split('.')[:-1]:
                model_relation = self.get_related_model(join_relation)
                query = query.join(model_relation)
                # redefine order column name, because relationship can have a different name
                # from the related table name.
                tmp_order_column = tmp_order_column + model_relation.__tablename__ + '.' 
            order_column = tmp_order_column + order_column.split('.')[-1]

        pk_column = self.get_pk_column()
        query_count = self.session.query(pk_column)
        query_count = self._get_base_query(query=query_count,
                                           filters=filters)
        query_count = self.session.query(func.count('*')).select_from(query_count.distinct().subquery())
        count = query_count.scalar()
        query = self._get_base_query(query=query,
                                     filters=filters,
                                     order_column=order_column,
                                     order_direction=order_direction)


        if page:
            query = query.offset(page * page_size)
        if page_size:
            query = query.limit(page_size)

        return count, query.all()

    def get_filters(self, search_columns=None):
        search_columns = search_columns or []
        return SupersetFilters(self.filter_converter_class, self, search_columns)

    def get_all_string_columns(self):
        all_columns = self.get_columns_list()
        return filter(lambda x: self.is_string(x), all_columns)

