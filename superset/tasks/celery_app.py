# -*- coding:utf-8 -*-
# __author__ = majing

# pylint: disable=C,R,W

"""Utility functions used across Superset"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from celery.schedules import crontab

from superset import app
from superset.utils import get_celery_app

config = app.config
app = get_celery_app(config)