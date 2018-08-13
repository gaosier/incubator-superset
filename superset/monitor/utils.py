# -*- coding:utf-8 -*-
# __author__ = majing
import os
import subprocess
import time

from collections import defaultdict

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


def restart_celery():
    is_success = 'undefined'
    msg = ''
    old_pids = {}
    try:
        old_pids = get_celery_beat_worker_pid()

        # kill old worker,beat
        kill_cmd = ['pkill',  '-9',  '-f', 'celery']
        subprocess.Popen(kill_cmd)

        cmd_beat = 'celery --workdir=%s -A superset.celery_app beat -s celerybeat-schedule'
        cmd_worker = 'celery multi start worker --workdir=%s -A superset.celery_app --loglevel=INFO  -D  --concurrency=4 --pidfile=%s --logfile=%s'

        for cmd in [cmd_beat, cmd_worker]:
            cmd_beat_args = list(map(deal_cmd, cmd.split()))
            subprocess.Popen(cmd_beat_args)
            time.sleep(2)
    except Exception as exc:
        is_success = 'failed'
        msg = str(exc)

    return is_success, msg, old_pids