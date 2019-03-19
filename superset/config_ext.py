# -*-coding:utf-8-*-
import os
from werkzeug.contrib.cache import RedisCache

from superset.custom_user.sec import MySecurityManager

from superset.config import DATA_DIR

# flask-sqlalchemy config
SQLALCHEMY_DATABASE_URI = os.environ['KINGKONG_DB']
SQLALCHEMY_POOL_SIZE = 50
SQLALCHEMY_POOL_RECYCLE = 3600
SQLALCHEMY_MAX_OVERFLOW = 10

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
EMAIL_REPORTS_USER = 'admin'
EMAIL_REPORTS_SUBJECT_PREFIX = '数据分析报告-'
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
WEBDRIVER_BASEURL = 'http://kingkong.dev.aixuexi.com/'
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

# 表和透视表页面展示配置
NOT_GROUPBY_ROW_LIMIT = 1000       # 非聚合查询显示1000
GROUPBY_ROW_LIMIT = 1500           # 聚合查询显示1500