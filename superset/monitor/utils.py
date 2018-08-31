# -*- coding:utf-8 -*-
# __author__ = majing
import os
import subprocess
import logging
import json
import requests
import hashlib
import copy
from prettytable import PrettyTable


dir_name = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pid_file = os.path.join(dir_name, 'celery.pid')
log_file = os.path.join(dir_name, 'celery.log')
beat_pid_file = os.path.join(dir_name, 'celerybeat.pid')


def deal_cmd(command):
    info = {'--workdir': dir_name, '--pidfile': pid_file, '--logfile': log_file}

    if '%s' in command:
        _cm = command
        key, _ = _cm.split('=')
        command = command % info.get(key)
    return command


def get_pid(filepath):
    pid = -1
    if os.path.isfile(filepath):
        f = open(filepath)
        content = f.read().strip()
        pid = int(content)
    return pid


def get_celery_beat_worker_pid():
    pids = {}
    pids['beat'] = get_pid(beat_pid_file)
    pids['worker'] = get_pid(pid_file)
    return pids


def pkill_celery():
    kill_cmd = ['pkill',  '-9',  '-f', 'celery']
    subprocess.Popen(kill_cmd)


def restart_celery_beat():
    cmd_beat = 'celery --workdir=%s -A superset.celery_app beat -s celerybeat-schedule'
    cmd_beat_args = list(map(deal_cmd, cmd_beat.split()))
    subprocess.Popen(cmd_beat_args)


def restart_celery_worker():
    cmd_worker = 'celery multi start worker --workdir=%s -A superset.celery_app --loglevel=INFO  -D  --concurrency=4 --pidfile=%s --logfile=%s'
    cmd_work_args = list(map(deal_cmd, cmd_worker.split()))
    subprocess.Popen(cmd_work_args)


def report_template(*args):
    html = u"""
    <!DOCTYPE html PUBLIC '-//W3C//DTD XHTML 1.0 Transitional//EN' 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'>
    <html xmlns='http://www.w3.org/1999/xhtml'>
        <head>

        　　<meta http-equiv='Content-Type' content="text/html; charset=UTF-8" />

        　　<title>数仓监控</title>

        　　<meta name="viewport" content="width=device-width, initial-scale=1.0"/>

        </head>
        <style>
          table {
            border-collapse: collapse;
          }
          th, td {
            border: 1px solid #ccc;
            padding: 10px;
            text-align: left;
          }
          tr:nth-child(even) {
            background-color: #eee;
          }
          tr:nth-child(odd) {
            background-color: #fff;
          }            
        </style>

        <body style="margin: 0; padding: 0;">
             <h2 style="color:red"> [%s]数据校验结果 </h2>
        　　　<p style="color:green"> 定时任务运行记录： <p>%s</P> </p>
             <p style="color:green"> 校验记录：<p>%s</p> </p>
        </body>

    </html>


    """ % args
    return html


def send_mail(content, to_mails):
    if isinstance(to_mails, str):
        to_mails = to_mails.split(',')

    logging.info(u"to_mails: %s" % to_mails)

    for mail in to_mails:
        form_data = {"businessType":"spider_monitor",
                    "operatorId":1,
                    "para":{"content": content},
                    "subject": u"数仓监控",
                    "templateCode":"MAIL_BI_Monitor",
                    "toMails": [mail]
                }
        form_data['sign'] = _get_sign(form_data)
        resp = _send_mail(form_data)
        if resp.status_code != 200:
            raise ValueError("send email error: %s,   users: %s" % (resp.content, to_mails))


def _get_sign(form_data):
    tag_list = ['mailSend']
    tag_list.append(form_data['subject'])
    tag_list.append(form_data['templateCode'])
    tag_list.append(json.dumps(form_data['toMails']))
    if 'operatorId' in form_data:
        tag_list.append(str(form_data['operatorId']))
    if 'businessType' in form_data:
        tag_list.append(form_data['businessType'])

    m2 = hashlib.md5()
    tag_str = ':'.join(tag_list)
    print(tag_str)
    m2.update(tag_str.encode('utf-8'))
    sign = m2.hexdigest()
    return sign


def _send_mail(mail_data):
    url = 'http://api.aixuexi.com/middleware/mail/mailSend'
    headers = {'Content-Type': 'application/json'}
    resp = requests.post(url, data=json.dumps(mail_data).encode('utf-8'), headers=headers)
    return resp


def to_html(columns, instances, is_need_parse=False):
    """
    输出一个table html
    """
    if not columns:
        raise ValueError(u'参数columns不能为空')

    values = []
    _table = PrettyTable()
    _table.field_names = columns

    if is_need_parse:
        try:
            for task in instances:
                _tmp = []
                for key in columns:
                    _tmp.append(getattr(task, key))
                values.append(_tmp)
        except Exception as exc:
            raise ValueError(str(exc))
    else:
        values = instances

    for item in values:
        _table.add_row(item)

    return _table.get_html_string()


"""
 Logging configuration
"""
log_file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "celery.log")
logger = logging.getLogger('monitor')
hander = logging.handlers.TimedRotatingFileHandler(filename=log_file_path, when='D',
                                                   interval=1, backupCount=7)
fmt = '%(asctime)s  %(levelname)s  %(filename)s:%(lineno)s  %(funcName)s  %(message)s'

formatter = logging.Formatter(fmt)
hander.setFormatter(formatter)
logger.addHandler(hander)
logger.setLevel(logging.INFO)

tr_html = "<span style='color:red'>表[sync_data.ods_page] 字段[uid]没有错误值</span>"
tr_html_1 = "<span style='color:green'>字段[pd]没有错误值<br></span>"

test_html = """
%s <br>

%s <br>

字段[pad]在分区["(pt&gt;='2018_08_30' and pt&lt;'2018_08_31')"]中有错误值<br>

字段[st]没有错误值<br>
"""  % (tr_html, tr_html_1)


table_html = """
<table>
<tbody><tr>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">
任务名称</td>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">
校验规则</td>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">
校验类型</td>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">
执行结果</td>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">
详情</td>
</tr>
<tr>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">
埋点数据错误校验任务</td>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">
埋点数据校验</td>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">
error</td>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">
True</td>
<td align="left" style="text-align:justify;padding:10px;border:1px solid #CCCCCC;">

%s  
</td>
</tr>
</tbody></table>

"""  % test_html


