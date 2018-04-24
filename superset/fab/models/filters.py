#-*-coding:utf-8-*-
from sqlalchemy.sql import union_all

from flask_appbuilder.models.filters import Filters


class SupersetFilters(Filters):

    def _apply_flt(self, flt,value):
        pass

    def apply_all(self, query):
        tag = False
        querys = []
        for flt, value in zip(self.filters, self.values):
            if type(query) == type([]):
                bak_query = []
                for q in query:
                    q2 = flt.apply(q, value)
                    assert(type(q2) != type([]))
                    bak_query.append(q2)
                query = bak_query
            else:
                query = flt.apply(query, value)
                if type(query) == type([]):
                    tag = True
        if tag:
            #return self.datamodel.session.query(union_all(query))
            querys = query
            q0 = None
            for i in range(0, len(querys)):
                if i == 0:
                    q0 = querys[i]
                else:
                    q0 = q0.union_all(querys[i])
            return q0
        else:
            return query


    def get_joined_filters(self, filters):
        """
            Creates a new filters class with active filters joined
        """
        retfilters = SupersetFilters(self.filter_converter, self.datamodel)
        retfilters.filters = self.filters + filters.filters
        retfilters.values = self.values + filters.values
        return retfilters

    def add_filter_index(self, column_name, filter_instance_index, value):
        """
        重写该方法是为了解决当分类与releated_view联合使用出现的bug
        """
        try:
            self._add_filter(self._all_filters[column_name][filter_instance_index], value)
        except:
            pass
