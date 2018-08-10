# -*- coding:utf-8 -*-
# __author__ = majing
from flask_appbuilder.validators import ValidationError
from wtforms.validators import Length


class SchedulerCheck(object):
    """
    check scheduler
    
    :param message:
        Error message to raise in case of a validation error.
    """
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if field.data:
            interval = field.data.split()
            if len(interval) != 5:
                message = self.message
                if message is None:
                    message = "interval 格式错误，请使用crontab格式"

                raise ValidationError(message)
        else:
            raise ValidationError("interval不能为空")