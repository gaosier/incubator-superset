#-*-coding:utf-8-*-
import os
import wrapcache
from werkzeug.contrib.cache import RedisCache
SQLALCHEMY_DATABASE_URI = os.environ['KINGKONG_DB']

class CeleryConfig(object):
    BROKER_URL = 'redis://localhost:6379/1'
    CELERY_IMPORTS = ('superset.sql_lab', )
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'
    CELERY_ANNOTATIONS = {'tasks.add': {'rate_limit': '10/s'}}
    CELERYD_LOG_LEVEL = 'DEBUG'
    CELERYD_PREFETCH_MULTIPLIER = 1 
    CELERY_ACKS_LATE = True
CELERY_CONFIG = CeleryConfig
RESULTS_BACKEND = RedisCache(
            host='localhost', port=6379, key_prefix='superset_results')
