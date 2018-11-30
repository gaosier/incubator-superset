# -*- coding:utf-8 -*-
# __author__ = majing
"""
处理模型运行过程中的日志
"""
import logging
import os
import requests

from jinja2 import Template


def mkdirs(path, mode):
    """
    Creates the directory specified by path, creating intermediate directories
    as necessary. If directory already exists, this is a no-op.

    :param path: The directory to create
    :type path: str
    :param mode: The mode to give to the directory e.g. 0o755, ignores umask
    :type mode: int
    """
    try:
        o_umask = os.umask(0)
        os.makedirs(path, mode)
    except OSError:
        if not os.path.isdir(path):
            raise
    finally:
        os.umask(o_umask)


class FileTaskHandler(logging.Handler):
    """
    FileTaskHandler is a python log handler that handles and reads
    task instance logs. It creates and delegates log handling
    to `logging.FileHandler` after receiving task instance context.
    It reads logs from task instance's host machine.
    """

    def __init__(self, base_log_folder, filename_template, filename):
        """
        :param base_log_folder: Base log folder to place logs.
        :param filename_template: template filename string
        """
        super(FileTaskHandler, self).__init__()
        self.handler = None
        self.local_base = base_log_folder
        self.filename_template = filename_template
        self.filename_jinja_template = None
        self.filename = filename
        self.log_path = None

        if "{{" in self.filename_template: #jinja mode
            self.filename_jinja_template = Template(self.filename_template)

    def set_context(self, instance_id):
        """
        Provide task_instance context to airflow task handler.
        :param ti: task instance object
        """
        local_loc = self._init_file(instance_id)
        self.handler = logging.FileHandler(local_loc)
        self.handler.setFormatter(self.formatter)
        self.handler.setLevel(self.level)
        self.log_path = local_loc

    def emit(self, record):
        if self.handler is not None:
            self.handler.emit(record)

    def flush(self):
        if self.handler is not None:
            self.handler.flush()

    def close(self):
        if self.handler is not None:
            self.handler.close()

    def _render_filename(self, instance_id):
        return self.filename_template.format(instance_id=instance_id, filename=self.filename)

    def _read(self, instance_id):
        """
        Template method that contains custom logic of reading
        logs given the try_number.
        :param ti: task instance record
        :return: log message as a string
        """
        # Task instance here might be different from task instance when
        # initializing the handler. Thus explicitly getting log location
        # is needed to get correct log path.
        log_relative_path = self._render_filename(instance_id)
        location = os.path.join(self.local_base, log_relative_path)

        log = ""

        if os.path.exists(location):
            try:
                with open(location) as f:
                    log += "*** Reading local log.\n" + "".join(f.readlines())
            except Exception as e:
                log = "*** Failed to load local log file: {}. {}\n".format(location, str(e))
        else:
            log += "*** Failed to load local log file: {} not exists\n".format(location)

        return log

    def read(self, instance_id, try_number=1):
        """
        Read logs of given task instance from local machine.
        :param task_instance: task instance object
        :return: a list of logs
        """
        # Task instance increments its try number when it starts to run.
        # So the log for a particular task try will only show up when
        # try number gets incremented in DB, i.e logs produced the time
        # after cli run and before try_number + 1 in DB will not be displayed.

        try_numbers = [try_number]

        logs = [''] * len(try_numbers)
        for i, try_number in enumerate(try_numbers):
            logs[i] += self._read(instance_id)

        return logs

    def _init_file(self, instance_id):
        """
        Create log directory and give it correct permissions.
        :param ti: task instance object
        :return relative log path of the given task instance
        """
        # To handle log writing when tasks are impersonated, the log files need to
        # be writable by the user that runs the Airflow command and the user
        # that is impersonated. This is mainly to handle corner cases with the
        # SubDagOperator. When the SubDagOperator is run, all of the operators
        # run under the impersonated user and create appropriate log files
        # as the impersonated user. However, if the user manually runs tasks
        # of the SubDagOperator through the UI, then the log files are created
        # by the user that runs the Airflow command. For example, the Airflow
        # run command may be run by the `airflow_sudoable` user, but the Airflow
        # tasks may be run by the `airflow` user. If the log files are not
        # writable by both users, then it's possible that re-running a task
        # via the UI (or vice versa) results in a permission error as the task
        # tries to write to a log file created by the other user.
        relative_path = self._render_filename(instance_id)
        full_path = os.path.join(self.local_base, relative_path)
        directory = os.path.dirname(full_path)
        # Create the log file and give it group writable permissions
        # TODO(aoen): Make log dirs and logs globally readable for now since the SubDag
        # operator is not compatible with impersonation (e.g. if a Celery executor is used
        # for a SubDag operator and the SubDag operator has a different owner than the
        # parent DAG)
        if not os.path.exists(directory):
            # Create the directory as globally writable using custom mkdirs
            # as os.makedirs doesn't set mode properly.
            mkdirs(directory, 0o775)

        if not os.path.exists(full_path):
            open(full_path, "a").close()
            # TODO: Investigate using 444 instead of 666.
            os.chmod(full_path, 0o666)

        return full_path

# ################# online analysis log config ###############
if os.environ.get("ONLINE_ANALYSIS_LOG"):
    ANALYSIS_LOG_DIR = os.environ.get("ONLINE_ANALYSIS_LOG")
else:
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    ANALYSIS_LOG_DIR = os.path.join(BASE_DIR, '/online-logs')


ana_code_logger = logging.getLogger('analysis.code')
ana_code_logger.setLevel(logging.INFO)
handler = FileTaskHandler(ANALYSIS_LOG_DIR, "{id}/{filename}.log", "code")
formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s [%(funcName)s]:%(lineno)s  %(message)s')
handler.setFormatter(formatter)
handler.name = "code"
ana_code_logger.addHandler(handler)

ana_param_logger = logging.getLogger('analysis.param')
ana_param_logger.setLevel(logging.INFO)
handler = FileTaskHandler(ANALYSIS_LOG_DIR, "{id}/{filename}.log", "param")
formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s [%(funcName)s]:%(lineno)s  %(message)s')
handler.setFormatter(formatter)
handler.name = "param"
ana_param_logger.addHandler(handler)

ana_image_logger = logging.getLogger('analysis.image')
ana_image_logger.setLevel(logging.INFO)
handler = FileTaskHandler(ANALYSIS_LOG_DIR, "{id}/{filename}.log", "image")
formatter = logging.Formatter('%(asctime)s  %(filename)s : %(levelname)s [%(funcName)s]:%(lineno)s  %(message)s')
handler.setFormatter(formatter)
handler.name = "image"
ana_image_logger.addHandler(handler)

# ################ end ############################################
