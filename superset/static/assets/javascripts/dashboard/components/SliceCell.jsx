/* eslint-disable react/no-danger */
import React from 'react';
import PropTypes from 'prop-types';

import { t } from '../../locales';
import { getExploreUrl } from '../../explore/exploreUtils';
import { exportSlice, hasSvg } from '../../components/ExportSlice';

const propTypes = {
  slice: PropTypes.object.isRequired,
  removeSlice: PropTypes.func.isRequired,
  expandedSlices: PropTypes.object,
};

function SliceCell({ expandedSlices, removeSlice, slice }) {
  return (
    <div className="slice-cell" id={`${slice.slice_id}-cell`}>
      <div className="chart-header">
        <div className="row">
          <div className="col-md-12 header">
            <span>{slice.slice_name}</span>
          </div>
          <div className="col-md-12 chart-controls">
            <div className="pull-right">
              {/*<a title={t('Move chart')} data-toggle="tooltip">*/}
              <a title={"移动图标位置"} data-toggle="tooltip">
                <i className="fa fa-arrows drag" />
              </a>
              {/*<a className="refresh" title={t('Force refresh data')} data-toggle="tooltip">*/}
              <a className="refresh" title={"点击刷新数据"} data-toggle="tooltip">
                <i className="fa fa-repeat" />
              </a>
              {slice.description &&
                <a title={t('Toggle chart description')}>
                  <i
                    className="fa fa-info-circle slice_info"
                    title={slice.description}
                    data-toggle="tooltip"
                  />
                </a>
              }
              <a
                href={slice.edit_url}
                // title={t('Edit chart')}
                title={"编辑切片"}
                data-toggle="tooltip"
              >
                <i className="fa fa-pencil" />
              </a>
              {/*<a href={getExploreUrl(slice.form_data, 'csv')} title={t('Export CSV')} data-toggle="tooltip">*/}
              <a href={getExploreUrl(slice.form_data, 'xlsx')} title={"导出数据"} data-toggle="tooltip">
                <i className="fa fa-table" />
              </a>
              {/*<a href={getExploreUrl(slice.form_data)} title={t('Explore chart')} data-toggle="tooltip">*/}
              <a href={getExploreUrl(slice.form_data)} title={"跳转至切片"} data-toggle="tooltip">
                <i className="fa fa-share" />
              </a>
              <a
                 className="exportPNG"
                 onClick={() => { exportSlice(slice, 'png'); }}
                 title="下载图片"
                 data-toggle="tooltip"
                 style={{ display: hasSvg(slice) ? 'inline' : 'none' }}
               >
                 <i className="fa fa-download" />
               </a>
              <a
                className="remove-chart"
                // title={t('Remove chart from dashboard')}
                title={"将图表移除看板"}
                data-toggle="tooltip"
              >
                <i
                  className="fa fa-close"
                  onClick={() => { removeSlice(slice.slice_id); }}
                />
              </a>
            </div>
          </div>
        </div>
      </div>
      <div
        className="slice_description bs-callout bs-callout-default"
        style={
          expandedSlices &&
          expandedSlices[String(slice.slice_id)] ? {} : { display: 'none' }
        }
        dangerouslySetInnerHTML={{ __html: slice.description_markeddown }}
      />
      <div className="row chart-container">
        <input type="hidden" value="false" />
        <div id={'token_' + slice.slice_id} className="token col-md-12">
          <img
            src="/static/assets/images/loading.gif"
            className="loading"
            alt="loading"
          />
          <div
            id={'con_' + slice.slice_id}
            className={`slice_container ${slice.form_data.viz_type}`}
          />
        </div>
      </div>
    </div>
  );
};

SliceCell.propTypes = propTypes;

export default SliceCell;
