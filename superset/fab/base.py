#-*-coding:utf-8-*-
from .filters import SupersetTemplateFilters
from flask_appbuilder import AppBuilder


class SupersetAppBuilder(AppBuilder):

    def _add_global_filters(self):
        self.template_filters = SupersetTemplateFilters(self.get_app, self.sm)

