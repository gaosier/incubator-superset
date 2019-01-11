#-*-coding:utf-8-*-
import re
from flask import request

from flask_appbuilder.urltools import *


def get_superset_filter_args(filters):
    filters.clear_filters()
    for arg, vl in request.args.lists():
        re_match = re.findall('_flt_(\d)_(.*)', arg)
        if len(vl) == 1:
            vl = vl[0]

            if re_match:
                filters.add_filter_index(re_match[0][1], int(re_match[0][0]), vl)
        else:
            for item in vl:
                if re_match:
                    filters.add_filter_index(re_match[0][1], int(re_match[0][0]), item)


def get_page_args():
    """
        Get page arguments, returns a dictionary
        { <VIEW_NAME>: PAGE_NUMBER }

        Arguments are passed: page_<VIEW_NAME>=<PAGE_NUMBER>

    """
    pages = {}
    for arg in request.args:
        re_match = re.findall('^page_(.*)', arg)
        if re_match:
            pages[re_match[0]] = int(request.args.get(arg))
    return pages


