#-*-coding:utf-8-*-
from .filters import SupersetTemplateFilters
from flask_appbuilder import AppBuilder


class SupersetAppBuilder(AppBuilder):

    def _add_global_filters(self):
        self.template_filters = SupersetTemplateFilters(self.get_app, self.sm)

    def _process_inner_views(self):
        for view in self.baseviews:
            for inner_class in view.get_uninit_inner_views():
                for v in self.baseviews:
                    if isinstance(v, inner_class) and v not in view.get_init_inner_views() and v.__class__ is inner_class:
                        view.get_init_inner_views().append(v)

