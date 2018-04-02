#-*-coding:utf-8-*-
from datetime import datetime, timedelta
import json
import logging
import os
import re
import time
import traceback
from urllib import parse
from urllib.parse import quote

from flask import (
     g, request, redirect, flash, Response, render_template, Markup,
    abort, url_for,send_from_directory,send_file)

from superset import (
    app, appbuilder, cache, db, results_backend, security, sm, sql_lab, utils,
    viz,
)
from superset.utils import (
    has_access, merge_extra_filters, merge_request_params, QueryStatus,
)
import superset.models.core as models
from superset.models.sql_lab import Query
import xlsxwriter

from flask_appbuilder import expose, SimpleFormView

from .base import (
    api, BaseSupersetView, CsvResponse, DeleteMixin,
    generate_download_headers, get_error_msg, get_user_roles,
    json_error_response, SupersetFilter, SupersetModelView, YamlExportMixin,
)

config = app.config
stats_logger = config.get('STATS_LOGGER')
log_this = models.Log.log_this
sqllab_data_dir = config.get('SQLLAB_DATA_DIR')


class SupersetExt(BaseSupersetView):
    @has_access
    @expose("/xlsx/<client_id>")
    @log_this
    def xlsx(self, client_id):
        """Download the query results as xlsx."""
        logging.info("Exporting XLSX file [{}]".format(client_id))
        query = (
            db.session.query(Query)
            .filter_by(client_id=client_id)
            .one()
        )

        rejected_tables = self.rejected_datasources(
            query.sql, query.database, query.schema)
        if rejected_tables:
            flash(get_datasource_access_error_msg('{}'.format(rejected_tables)))
            return redirect('/')
        blob = None
        if results_backend and query.results_key:
            logging.info(
                "Fetching XLSX from results backend "
                "[{}]".format(query.results_key))
            blob = results_backend.get(query.results_key)
        filename = query.name + u'.xlsx'
        filepath = os.path.join(sqllab_data_dir, filename)
        if blob:
            logging.info("Decompressing")
            json_payload = utils.zlib_decompress_to_string(blob)
            obj = json.loads(json_payload)
            columns = [c['name'] for c in obj['columns']]
            df = pd.DataFrame.from_records(obj['data'], columns=columns)
            logging.info("Using pandas to convert to XLSX")
            df.to_excel(filepath, index=False, encoding='utf-8', engine='xlsxwriter')
        else:
            logging.info("Running a query to turn into XLSX")
            sql = query.select_sql or query.executed_sql
            df = query.database.get_df(sql, query.schema)
            # TODO(bkyryliuk): add compression=gzip for big files.
            df.to_excel(filepath, index=False, encoding='utf-8', engine='xlsxwriter')
        return send_file(filepath, as_attachment=True, 
                attachment_filename=quote(filename))


appbuilder.add_view_no_menu(SupersetExt)


