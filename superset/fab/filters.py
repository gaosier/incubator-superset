#-*-coding:utf-8-*-
from flask import request, url_for

from flask_appbuilder.filters import TemplateFilters,app_template_filter


class SupersetTemplateFilters(TemplateFilters):


    @app_template_filter('link_page')
    def link_page_filter(self, page, modelview_name):
        """
            Arguments are passed like: page_<VIEW_NAME>=<PAGE_NUMBER>
        """
        new_args = request.view_args.copy()
        args = request.args.copy()
        args['page_' + modelview_name] = page
        args_list =[]
        tmp_list = []
        for arg, vl in args.lists():
            i = 0
            for v in vl:
                if i == 0:
                    args_list.append((arg,vl[0]))
                else:
                    tmp_list.append((arg,v))
                i += 1
        url = url_for(request.endpoint, **dict(list(new_args.items()) + args_list))
        for arg,v in tmp_list:
            url += '&{0}={1}'.format(arg,v)
        return url
