#-*- coding:utf-8-*-
from flask_appbuilder.models.sqla.filters import *
from flask_appbuilder.models.sqla.filters import FilterNotContains,get_field_setup_query
from flask_appbuilder.models.filters import FilterRelation
from flask_babel import lazy_gettext

from sqlalchemy.sql import func


class FilterRelationManyToManyEqual(FilterRelation):
    name = lazy_gettext('Relation as Many')

    def apply(self, query, value):
        is_count = False
        if 'SELECT count(%s) AS count_1' in str(query):
            is_count = True
        if type(value) != type([]):
            value = [value]
        q0 = self._get_union_query(query, value)
        return q0 if len(q0)>1 else q0[0]

    def _get_union_query(self, query, values):
        querys = []
        for v in values:
            query_bak, field = get_field_setup_query(query, self.model, self.column_name)
            rel_obj = self.datamodel.get_related_obj(self.column_name, v)
            query0=query_bak.filter(field.contains(rel_obj))
            querys.append(query0)
        return querys


class SuperSetSQLAFilterConverter(SQLAFilterConverter):
    """
        Class for converting columns into a supported list of filters
        specific for SQLAlchemy.

    """
    conversion_table = (('is_relation_many_to_one', [FilterRelationOneToManyEqual,
                        FilterRelationOneToManyNotEqual]),
                        ('is_relation_one_to_one', [FilterRelationOneToManyEqual,
                        FilterRelationOneToManyNotEqual]),
                        ('is_relation_many_to_many', [FilterRelationManyToManyEqual]),
                        ('is_relation_one_to_many', [FilterRelationManyToManyEqual]),
                        ('is_enum', [FilterEqual,
                                     FilterNotEqual]),
                        ('is_text', [FilterStartsWith,
                                     FilterEndsWith,
                                     FilterContains,
                                     FilterEqual,
                                     FilterNotStartsWith,
                                     FilterNotEndsWith,
                                     FilterNotContains,
                                     FilterNotEqual]),
                        ('is_string', [FilterStartsWith,
                                       FilterEndsWith,
                                       FilterContains,
                                       FilterEqual,
                                       FilterNotStartsWith,
                                       FilterNotEndsWith,
                                       FilterNotContains,
                                       FilterNotEqual]),
                        ('is_integer', [FilterEqual,
                                        FilterGreater,
                                        FilterSmaller,
                                        FilterNotEqual]),
                        ('is_float', [FilterEqual,
                                      FilterGreater,
                                      FilterSmaller,
                                      FilterNotEqual]),
                        ('is_numeric', [FilterEqual,
                                      FilterGreater,
                                      FilterSmaller,
                                      FilterNotEqual]),
                        ('is_date', [FilterEqual,
                                     FilterGreater,
                                     FilterSmaller,
                                     FilterNotEqual]),
                        ('is_boolean', [FilterEqual,
                                        FilterNotEqual]),
                        ('is_datetime', [FilterEqual,
                                         FilterGreater,
                                         FilterSmaller,
                                         FilterNotEqual]),
    )



