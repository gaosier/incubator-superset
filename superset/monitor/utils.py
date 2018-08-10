# -*- coding:utf-8 -*-
# __author__ = majing
import os
import sys
import subprocess

dir_name = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
pid_file = os.path.join(dir_name, 'celery.pid')
log_file = os.path.join(dir_name, 'celery.log')


def deal_cmd(command):
    info = {'--workdir': dir_name, '--pidfile': pid_file, '--logfile': log_file}

    if '%s' in command:
        _cm = command
        key, _ = _cm.split('=')
        command = command % info.get(key)
    return command


def restart_celery():
    cmd_beat = 'celery --workdir=%s -A superset.celery_app beat -s celerybeat-schedule'
    cmd_worker = 'celery multi start worker --workdir=%s -A superset.celery_app --loglevel=INFO  -D  --concurrency=4 --pidfile=%s --logfile=%s'

    cmd_beat_args = list(map(deal_cmd, cmd_beat.split()))
    print("cmd_beat_args:  %s" % cmd_beat_args)
    r = subprocess.Popen(cmd_beat_args, stdout=sys.stdout, stderr=sys.stderr)
    print("result:    r: %s    dir(r): %s" % (r, dir(r)))
    print("reslut:   r.returncode:%s    r.stderr:%s    r.errors: %s " % (r.returncode, r.stderr, r.errors))

    cmd_worker_args = list(map(deal_cmd, cmd_worker.split()))
    print("cmd_worker_args:  %s" % cmd_worker_args)
    rw = subprocess.Popen(cmd_worker_args, stdout=sys.stdout, stderr=sys.stderr)
    print("reslut:   r.returncode:%s    r.stderr:%s    r.errors: %s " % (rw.returncode, rw.stderr, rw.errors))
    return True, 'restart beat and worker success '