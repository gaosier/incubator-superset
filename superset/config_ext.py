#-*-coding:utf-8-*-
import os
from celery.schedules import crontab
from werkzeug.contrib.cache import RedisCache

from superset.custom_user.sec import MySecurityManager

from superset.config import DATA_DIR

SQLALCHEMY_DATABASE_URI = os.environ['KINGKONG_DB']
APP_ICON = "/static/assets/images/logo.png" 


class CeleryConfig(object):
    BROKER_URL = 'redis://localhost:6379/0'
    CELERY_IMPORTS = ('superset.sql_lab', )
    CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

    CELERYD_LOG_LEVEL = 'DEBUG'
    CELERYD_PREFETCH_MULTIPLIER = 1 
    CELERY_ACKS_LATE = True

    CELERY_ANNOTATIONS = {
        'sql_lab.get_sql_results': {
            'rate_limit': '100/s',
        },
        'email_reports.send': {
            'rate_limit': '1/s',
            'time_limit': 120,
            'soft_time_limit': 150,
            'ignore_result': True,
        },
    }
    CELERYBEAT_SCHEDULE = {
        'email_reports.schedule_hourly': {
            'task': 'email_reports.schedule_hourly',
            'schedule': crontab(minute=5, hour='*'),
        },
    }


CELERY_CONFIG = CeleryConfig
RESULTS_BACKEND = RedisCache(
            host='localhost', port=6379, key_prefix='superset_results')

SQLLAB_DATA_DIR = os.path.join(DATA_DIR, 'sqllab')
if not os.path.exists(SQLLAB_DATA_DIR):
    os.makedirs(SQLLAB_DATA_DIR)

CUSTOM_SECURITY_MANAGER = MySecurityManager
SUPERSET_MEMCACHED={
    'servers':('m-2ze017afe9b6b9d4.memcache.rds.aliyuncs.com:11211'),
    'username':'f8ed3954cee74f46',
    'password':'Gaosi2012'
}

BABEL_DEFAULT_LOCALE = 'zh'

ENABLE_SCHEDULED_EMAIL_REPORTS = True
EMAIL_REPORTS_CRON_RESOLUTION = 1