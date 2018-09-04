# -*- coding:utf-8 -*-
# __author__ = majing

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import os
import functools
import json
import logging
import traceback
from datetime import datetime
from sqlalchemy import create_engine

import yaml
from flask import abort, flash, g, get_flashed_messages, redirect, Response
from flask_appbuilder import BaseView
from flask_appbuilder.actions import action
from flask_appbuilder.widgets import ListWidget
from flask_babel import get_locale
from flask_babel import gettext as __
from flask_babel import lazy_gettext as _
from odps import ODPS

from superset.views.base import SupersetModelView as ModelView
from superset import conf, security_manager, utils
from superset.translations.utils import get_language_pack
from superset.config_ext import SQLALCHEMY_DATABASE_URI

FRONTEND_CONF_KEYS = (
    'SUPERSET_WEBSERVER_TIMEOUT',
    'ENABLE_JAVASCRIPT_CONTROLS',
)


def get_error_msg():
    if conf.get('SHOW_STACKTRACE'):
        error_msg = traceback.format_exc()
    else:
        error_msg = 'FATAL ERROR \n'
        error_msg += (
            'Stacktrace is hidden. Change the SHOW_STACKTRACE '
            'configuration setting to enable it')
    return error_msg


def json_error_response(msg=None, status=500, stacktrace=None, payload=None):
    if not payload:
        payload = {'error': str(msg)}
        if stacktrace:
            payload['stacktrace'] = stacktrace
    return Response(
        json.dumps(payload, default=utils.json_iso_dttm_ser),
        status=status, mimetype='application/json')


def generate_download_headers(extension, filename=None):
    filename = filename if filename else datetime.now().strftime('%Y%m%d_%H%M%S')
    content_disp = 'attachment; filename={}.{}'.format(filename, extension)
    headers = {
        'Content-Disposition': content_disp,
    }
    return headers


def api(f):
    """
    A decorator to label an endpoint as an API. Catches uncaught exceptions and
    return the response in the JSON format
    """
    def wraps(self, *args, **kwargs):
        try:
            return f(self, *args, **kwargs)
        except Exception as e:
            logging.exception(e)
            return json_error_response(get_error_msg())

    return functools.update_wrapper(wraps, f)


def get_datasource_exist_error_mgs(full_name):
    return __('Datasource %(name)s already exists', name=full_name)


def get_user_roles():
    if g.user.is_anonymous():
        public_role = conf.get('AUTH_ROLE_PUBLIC')
        return [security_manager.find_role(public_role)] if public_role else []
    return g.user.roles


class BaseMonitorView(BaseView):
    def common_bootsrap_payload(self):
        """Common data always sent to the client"""
        messages = get_flashed_messages(with_categories=True)
        locale = str(get_locale())
        return {
            'flash_messages': messages,
            'conf': {k: conf.get(k) for k in FRONTEND_CONF_KEYS},
            'locale': locale,
            'language_pack': get_language_pack(locale),
        }


class MonitorListWidget(ListWidget):
    template = 'superset/fab_overrides/list.html'


class MonitorModelView(ModelView):
    page_size = 100
    list_widget = MonitorListWidget


class ListWidgetWithCheckboxes(ListWidget):
    """An alternative to list view that renders Boolean fields as checkboxes

    Works in conjunction with the `checkbox` view."""
    template = 'superset/fab_overrides/list_with_checkboxes.html'


def validate_json(form, field):  # noqa
    try:
        json.loads(field.data)
    except Exception as e:
        logging.exception(e)
        raise Exception(_("json isn't valid"))


class YamlExportMixin(object):
    @action('yaml_export', __('Export to YAML'), __('Export to YAML?'), 'fa-download')
    def yaml_export(self, items):
        if not isinstance(items, list):
            items = [items]

        data = [t.export_to_dict() for t in items]
        return Response(
            yaml.safe_dump(data),
            headers=generate_download_headers('yaml'),
            mimetype='application/text')


class DeleteMixin(object):
    def _delete(self, pk):
        """
            Delete function logic, override to implement diferent logic
            deletes the record with primary_key = pk

            :param pk:
                record primary key to delete
        """
        item = self.datamodel.get(pk, self._base_filters)
        if not item:
            abort(404)
        try:
            self.pre_delete(item)
        except Exception as e:
            flash(str(e), 'danger')
        else:
            view_menu = security_manager.find_view_menu(item.get_perm())
            pvs = security_manager.get_session.query(
                security_manager.permissionview_model).filter_by(
                view_menu=view_menu).all()

            schema_view_menu = None
            if hasattr(item, 'schema_perm'):
                schema_view_menu = security_manager.find_view_menu(item.schema_perm)

                pvs.extend(security_manager.get_session.query(
                    security_manager.permissionview_model).filter_by(
                    view_menu=schema_view_menu).all())

            if self.datamodel.delete(item):
                self.post_delete(item)

                for pv in pvs:
                    security_manager.get_session.delete(pv)

                if view_menu:
                    security_manager.get_session.delete(view_menu)

                if schema_view_menu:
                    security_manager.get_session.delete(schema_view_menu)

                security_manager.get_session.commit()

            flash(*self.datamodel.message)
            self.update_redirect()

    @action(
        'muldelete',
        __('Delete'),
        __('Delete all Really?'),
        'fa-trash',
        single=False,
    )
    def muldelete(self, items):
        if not items:
            abort(404)
        for item in items:
            try:
                self.pre_delete(item)
            except Exception as e:
                flash(str(e), 'danger')
            else:
                self._delete(item.id)
        self.update_redirect()
        return redirect(self.get_redirect())


ODPS_INFO = {
        "access_key": os.environ.get("ODPS_ACCESS_KEY"),
        "access_id": os.environ.get("ODPS_ACCESS_ID")
    }

common_odps = None


def get_odps():
    global common_odps
    if not common_odps:
        if not ODPS_INFO.get("access_id") or not ODPS_INFO.get("access_key"):
            raise ValueError(u"请设置系统变量[ODPS_ACCESS_KEY, ODPS_ACCESS_ID]")
        common_odps = ODPS(ODPS_INFO.get('access_id'), ODPS_INFO.get('access_key'), 'sync_data')
    return common_odps

engine = None


def get_engine():
    global engine
    if not engine:
        engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    return engine


