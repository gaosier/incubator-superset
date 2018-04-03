#-*-coding:utf-8-*-
from datetime import datetime

def time_grain_convert(frm_date, time_grain_sqla):
    '''切片时间分组，格式化中文
    '''
    if time_grain_sqla=='Time Column':
        if type(frm_date) == type(''):
            return frm_date
        else:
            return frm_date.strftime('%Y-%m-%d %H:%M:%S.%f')
    elif time_grain_sqla=='second':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d %H:%M:%S')
        return frm_date.strftime('%Y年%m月%d日%H时%M分%S秒')
    elif time_grain_sqla=='minute':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d %H:%M:%S')
        return frm_date.strftime('%Y年%m月%d日%H时%M分')
    elif time_grain_sqla=='hour':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d %H:%M:%S')
        return frm_date.strftime('%Y年%m月%d日%H时')
    elif time_grain_sqla=='day':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年{1}月{1}日'.format(frm_date.year, frm_date.month,frm_date.day)
    elif time_grain_sqla=='week':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年第{1}周'.format(frm_date.year,frm_date.strftime('%U'))
    elif time_grain_sqla=='month':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年{1}月'.format(frm_date.year, frm_date.month)
    elif time_grain_sqla=='quarter':
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
    elif time_grain_sqla=='year':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年'.format(frm_date.year)
    elif time_grain_sqla=='week_start_monday':
        if type(frm_date) == type(''):
            frm_date = datetime.strptime(frm_date, '%Y-%m-%d')
        return '{0}年第{1}周'.format(frm_date.year, frm_date.strftime('%W'))

