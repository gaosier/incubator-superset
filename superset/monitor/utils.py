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

        　　<title>%s</title>

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
             <h2> 数据校验结果 </h2>
        　　　<p> 定时任务运行记录：%s </p>
             <p> 校验记录：%s </p>
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
        if resp.status_code == 200:
            logging.info(u'send email to [%s] success' % mail)
        else:
            logging.error(u'send email to [%s] fail: %s ' % (mail, resp.content))


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
