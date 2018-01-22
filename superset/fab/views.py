#-*-coding:utf-8-*-
from flask_appbuilder import ModelView as MV
from DictObject import DictObject,DictObjectList

from .urltools import *


class SupersetModelView(MV):

    def _get_list_widget(self, filters,
                         actions=None,
                         order_column='',
                         order_direction='',
                         page=None,
                         page_size=None,
                         widgets=None,
                         **args):

        """ get joined base filter and current active filter for query """
        widgets = widgets or {}
        actions = actions or self.actions
        page_size = page_size or self.page_size
        if not order_column and self.base_order:
            order_column, order_direction = self.base_order
        joined_filters = filters.get_joined_filters(self._base_filters)
        count, lst = self.datamodel.query(joined_filters, order_column, order_direction, page=page, page_size=page_size)
        try:
            pk_column = self.datamodel.get_pk_column()
            bst = [] 
            for row in lst: 
                try: 
                    keys = row.keys()
                except:
                    break
                entity = {} 
                name = self.datamodel.obj.__tablename__ + '_' + pk_column.name
                for key in keys:
                    pos = key.find(self.datamodel.obj.__tablename__)
                    key1 = key[pos:]
                    if name == key1:
                        pk_name = key
                        break
                value = getattr(row, pk_name)
                entity[pk_column.name] = value
                bst.append(DictObject(entity))
            lst = bst if len(bst) !=0 else lst
            pks = self.datamodel.get_keys(lst)

            # serialize composite pks
            pks = [self._serialize_pk_if_composite(pk) for pk in pks]
            #from datetime import datetime
            #d1 = datetime.now()
            lst = self.datamodel.session.query(self.datamodel.obj).filter(pk_column.in_(pks))
            #d2 = datetime.now()
            #print(d2-d1)
        except:
            pass
        pks = self.datamodel.get_keys(lst)
        # serialize composite pks
        pks = [self._serialize_pk_if_composite(pk) for pk in pks]

        widgets['list'] = self.list_widget(label_columns=self.label_columns,
                                           include_columns=self.list_columns,
                                           value_columns=self.datamodel.get_values(lst, self.list_columns),
                                           order_columns=self.order_columns,
                                           formatters_columns=self.formatters_columns,
                                           page=page,
                                           page_size=page_size,
                                           count=count,
                                           pks=pks,
                                           actions=actions,
                                           filters=filters,
                                           modelview_name=self.__class__.__name__)
        return widgets

    """
    -----------------------------------------------------
            CRUD functions behaviour
    -----------------------------------------------------
    """
    def _list(self):
        """
            list function logic, override to implement different logic
            returns list and search widget
        """
        if get_order_args().get(self.__class__.__name__):
            order_column, order_direction = get_order_args().get(self.__class__.__name__)
        else:
            order_column, order_direction = '', ''
        page = get_page_args().get(self.__class__.__name__)
        page_size = get_page_size_args().get(self.__class__.__name__)
        get_superset_filter_args(self._filters)
        widgets = self._get_list_widget(filters=self._filters,
                                        order_column=order_column,
                                        order_direction=order_direction,
                                        page=page,
                                        page_size=page_size)
        form = self.search_form.refresh()
        self.update_redirect()
        return self._get_search_widget(form=form, widgets=widgets)


