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
    CELERY_IMPORTS = ('superset.sql_lab',)
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
    # CELERYBEAT_SCHEDULE = {
    #     'email_reports.schedule_hourly': {
    #         'task': 'email_reports.schedule_hourly',
    #         'schedule': crontab(minute=3, hour='*'),
    #     },
    # }


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
timezone = 'Asia/Shanghai'

# 邮件配置

# Enable / disable scheduled email reports
ENABLE_SCHEDULED_EMAIL_REPORTS = True
 # Email reports - minimum time resolution (in minutes) for the crontab
EMAIL_REPORTS_CRON_RESOLUTION = 15
 # Email report configuration
# From address in emails
EMAIL_REPORT_FROM_ADDRESS = 'reports@superset.org'
 # Send bcc of all reports to this address. Set to None to disable.
# This is useful for maintaining an audit trail of all email deliveries.
EMAIL_REPORT_BCC_ADDRESS = None
 # User credentials to use for generating reports
# This user should have permissions to browse all the dashboards and
# slices.
# TODO: In the future, login as the owner of the item to generate reports
EMAIL_REPORTS_USER = 'admin'
EMAIL_REPORTS_SUBJECT_PREFIX = '[Report] '
 # The webdriver to use for generating reports. Use one of the following
# firefox
#   Requires: geckodriver and firefox installations
#   Limitations: can be buggy at times
# chrome:
#   Requires: headless chrome
#   Limitations: unable to generate screenshots of elements
EMAIL_REPORTS_WEBDRIVER = 'chrome'
 # Window size - this will impact the rendering of the data
WEBDRIVER_WINDOW = {
    'dashboard': (1600, 2000),
    'slice': (3000, 1200),
}
 # Any config options to be passed as-is to the webdriver
WEBDRIVER_CONFIGURATION = {}
 # The base URL to query for accessing the user interface
WEBDRIVER_BASEURL = 'http://0.0.0.0:8088/'
SCHEDULED_EMAIL_DEBUG_MODE = False

# smtp server configuration
EMAIL_NOTIFICATIONS = False  # all the emails are sent using dryrun
SMTP_HOST = 'mail.gaosiedu.com'
SMTP_STARTTLS = True
SMTP_SSL = False
SMTP_USER = 'bj\\axxsyfxbg'
SMTP_PORT = 587
SMTP_PASSWORD = 'axxsyfxbg'
SMTP_MAIL_FROM = 'axxsyfxbg@gaosiedu.com'