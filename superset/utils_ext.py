#-*-coding:utf-8-*-
from datetime import datetime
from flask_babel import lazy_gettext as _

def time_grain_convert(frm_date, time_grain_sqla):
    '''切片时间分组，格式化中文
    '''
    if time_grain_sqla is None:
        if type(frm_date) == type(''):
            return frm_date
        else:
            return frm_date.strftime('%Y-%m-%d %H:%M:%S.%f')
    elif time_grain_sqla=='PT1S':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d %H:%M:%S')
        return frm_date.strftime('%Y年%m月%d日%H时%M分%S秒')
    elif time_grain_sqla=='PT1M':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d %H:%M:%S')
        return frm_date.strftime('%Y年%m月%d日%H时%M分')
    elif time_grain_sqla=='PT1H':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d %H:%M:%S')
        return frm_date.strftime('%Y年%m月%d日%H时')
    elif time_grain_sqla=='P1D':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年{1}月{2}日'.format(frm_date.year, frm_date.month,frm_date.day)
    elif time_grain_sqla=='P1W':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年第{1}周'.format(frm_date.year,frm_date.strftime('%U'))
    elif time_grain_sqla=='P1M':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年{1}月'.format(frm_date.year, frm_date.month)
    elif time_grain_sqla=='P0.25Y':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        if frm_date.month <=3:
            quarter = 1
        elif frm_date.month <=6:
            quarter = 2
        elif frm_date.month <=9:
            quarter = 3
        else:
            quarter = 4
        return '{0}年{1}季度'.format(frm_date.year, quarter)
    elif time_grain_sqla=='P1Y':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年'.format(frm_date.year)
    elif time_grain_sqla=='P1W':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年第{1}周'.format(frm_date.year, frm_date.strftime('%W'))

def metric_format(value, item):
    """
        #格式化生成sql_metric表对象时参数
    """
    table_name = str(item.table.table_name)
    if value == 'count_distinct':
        expression = 'COUNT(DISTINCT %s)'%(item.expression) if item.expression else 'COUNT(DISTINCT %s.%s)' % (table_name, item.column_name)
        verbose_name='%s(%s)'%(item.verbose_name or item.column_name,_('Count Distinct'))
    else:
        expression = "%s(%s)" % (value.upper(),item.expression)if item.expression else "%s(%s.%s)" % (value.upper(), table_name, item.column_name)
        verbose_name='%s(%s)'%(item.verbose_name or item.column_name , _(value.capitalize()))
    return {
        'metric_name': '%s__%s' % (value, item.column_name),
        'verbose_name': verbose_name,
        'metric_type': value,
        'expression': expression,
        'table_id': item.table_id
    }

def get_admin_id_list(db):
    """
    获取所有admin用户的id
    :return:
    """
    result = db.session.execute("select user_id from ab_user_role WHERE role_id=1")
    admin_user_list = []
    for i in result:
        admin_user_list.append(i[0])
    return admin_user_list
