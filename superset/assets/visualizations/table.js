import d3 from 'd3';
import dt from 'datatables.net-bs';
import 'datatables.net-bs/css/dataTables.bootstrap.css';

import { fixDataTableBodyHeight, d3TimeFormatPreset, d3format } from '../javascripts/modules/utils';
import './table.css';

const $ = require('jquery');

dt(window, $);

function tableVis(slice, payload) {
  const container = $(slice.selector);
  const fC = d3.format('0,000');

  const data = payload.data;
  const fd = slice.formData;

  let metrics = fd.metrics || [];
  // Add percent metrics
  metrics = metrics.concat((fd.percent_metrics || []).map(m => '%' + m));
  // Removing metrics (aggregates) that are strings
  metrics = metrics.filter(m => !isNaN(data.records[0][m]));
   // column on the top or metric on the top
  const combineMetric = fd.combine_metric;
  const cols = payload.data.columns;
  // get the metric of every column, with the consideration of combine_metric
  let metricForCols = cols;
  if (Array.isArray(cols[0])) {
    metricForCols = cols.map(col => combineMetric ?
      col[cols[0].length - 1] : col[0]);
  }
  const columnConfiguration = fd.column_configuration;
  const rowConfiguration = fd.row_configuration;
  // by default, column configution has high priority than row configuration
  const rowConfigHasHighPriority = fd.row_configuration_priority || false;

  function col(c) {
    const arr = [];
    for (let i = 0; i < data.records.length; i += 1) {
      arr.push(data.records[i][c]);
    }
    return arr;
  }
  const maxes = {};
  const mins = {};
  for (let i = 0; i < metrics.length; i += 1) {
    if (fd.align_pn) {
      maxes[metrics[i]] = d3.max(col(metrics[i]).map(Math.abs));
    } else {
      maxes[metrics[i]] = d3.max(col(metrics[i]));
      mins[metrics[i]] = d3.min(col(metrics[i]));
    }
  }
  const tsFormatter = d3TimeFormatPreset(fd.table_timestamp_format);

  const div = d3.select(slice.selector);
  div.html('');
  const table = div.append('table')
    .classed(
      'dataframe dataframe table table-striped ' +
      'table-condensed table-hover dataTable no-footer', true)
    .attr('width', '100%');

  const verboseMap = slice.datasource.verbose_map;
  // const cols = data.columns.map((c) => {
  //   if (verboseMap[c]) {
  //     return verboseMap[c];
  //   }
  //   // Handle verbose names for percents
  //   if (c[0] === '%') {
  //     const cName = c.substring(1);
  //     return '% ' + (verboseMap[cName] || cName);
  //   }
  //   return c;
  // });
    // to change the array to a string split by ','
  const transformToString = function (columnArray) {
    if (!Array.isArray(columnArray)) {
      return columnArray;
    } else if (columnArray.length > 1) {
      return columnArray.join(',');
    } else if (columnArray.length === 1) {
      return columnArray[0];
    }
    return '';
  };
  // check if the conditional config should add to the cell or not
  const checkAddOptionStyleOrnot = function (base, val, compare) {
    switch (compare) {
      case '<':
        return parseFloat(val) < parseFloat(base);
      case '=':
        return parseFloat(val) === parseFloat(base);
      case '>':
        return parseFloat(val) > parseFloat(base);
      case 'contains':
        return val.toString().indexOf(base) !== -1;
      case 'startsWith':
        return val.toString().startsWith(base);
      case 'endsWith':
        return val.toString().endsWith(base);
      default:
        return false;
    }
  };
   // check if the object is null or empty
  const checkObjectOrStringHasLengthOrnot = function (obj) {
    if (!obj) {
      return false;
    }
    if (typeof (obj) === 'string') {
      return obj.length > 0;
    } else if (typeof (obj) === 'object') {
      return Object.keys(obj).length > 0;
    }
    return true;
  };
   // check if this columnstring in column configuration or not
  // check if this option in this columnstring's config is null or not
  const findColInColumnConfigOption = function (columnString, configName) {
    if (columnString in columnConfiguration &&
      configName in columnConfiguration[columnString] &&
      checkObjectOrStringHasLengthOrnot(columnConfiguration[columnString][configName])
      ) {
      return true;
    }
    return false;
  };
   // to find the next column configure element in formdata used to set config
  const findNextColumnConfiguration = function (columnArray) {
    const length = columnArray.length;
    if (length > 1) {
      return columnArray.slice(0, length - 1);
    } else if (length === 1) {
      return columnArray[0];
    }
    return null;
  };
   // get column configuration of every option
  // if there are more than one configuration for this column and option
  // then get the more detailed one
  const getColumnConfigForOption = function (curColumn, configName) {
    let column = curColumn;
    let columnString = transformToString(column);
    while (Array.isArray(column) && column.length > 1 && !findColInColumnConfigOption(
        columnString, configName)) {
      column = findNextColumnConfiguration(column);
      columnString = transformToString(column);
    }
    if (!findColInColumnConfigOption(columnString, configName)) {
      return configName === 'bcColoringOption' || configName === 'coloringOption' ? {} : '';
    }
    return columnConfiguration[columnString][configName];
  };
   // get the column configuration object for the column
  const getColumnConfig = function (column) {
    const columnBgColorConfig = getColumnConfigForOption(column, 'bcColoringOption');
    const columnTextAlignConfig = getColumnConfigForOption(column, 'textAlign');
    const columnFormatConfig = getColumnConfigForOption(column, 'formatting');
    const columnComparisionConfig = getColumnConfigForOption(column, 'comparisionOption');
    const columnBasementConfig = getColumnConfigForOption(column, 'basement');
    const columnColorConfig = getColumnConfigForOption(column, 'coloringOption');
    const columnFontConfig = getColumnConfigForOption(column, 'fontOption');
     const columnConfig = {};
    columnConfig.columnBgColorConfig = columnBgColorConfig;
    columnConfig.columnFormatConfig = columnFormatConfig;
    columnConfig.columnTextAlignConfig = columnTextAlignConfig;
    columnConfig.columnComparisionConfig = columnComparisionConfig;
    columnConfig.columnBasementConfig = columnBasementConfig;
    columnConfig.columnColorConfig = columnColorConfig;
    columnConfig.columnFontConfig = columnFontConfig;
    return columnConfig;
  };
   // update the option in a config object
  const updateConfig = function (config, optionName, optionValue) {
    const newConfig = config;
    if (optionValue && checkObjectOrStringHasLengthOrnot(optionValue)) {
      newConfig[optionName] = optionValue;
    }
    return newConfig;
  };
   // update column configuration according to the cell's value
  const updateColumnConfig = function (obj, columnconfig, value) {
    let config = obj.data('config') || {};
    config = updateConfig(config, 'color', columnconfig.columnBgColorConfig);
    config = updateConfig(config, 'format', columnconfig.columnFormatConfig);
    config = updateConfig(config, 'textAlign', columnconfig.columnTextAlignConfig);
    if (checkAddOptionStyleOrnot(columnconfig.columnBasementConfig, value,
        columnconfig.columnComparisionConfig)) {
      config = updateConfig(config, 'color', columnconfig.columnColorConfig);
      config = updateConfig(config, 'fontWeight', columnconfig.columnFontConfig);
    }
    obj.data('config', config);
  };
   // apply color, font weight and format config to the cell
  const applyconfig = function (obj) {
    const config = obj.data('config') || {};
    const originalValue = obj.attr('initialValue');
    if (config.color && checkObjectOrStringHasLengthOrnot(config.color)) {
      obj.css('background', config.color.hex);
    }
    if (config.fontWeight && checkObjectOrStringHasLengthOrnot(config.fontWeight)) {
      obj.css('font-weight', config.fontWeight);
    }
    if (config.textAlign && checkObjectOrStringHasLengthOrnot(config.textAlign)) {
      obj.css('text-align', config.textAlign);
    }
    if (config.format && checkObjectOrStringHasLengthOrnot(config.format)) {
      if (originalValue !== '') {
        obj.html(d3.format(config.format)(originalValue));
      }
    }
  };
   // check if this row has row configuration or not
  const getRowConfig = function (obj) {
    const rowContains = rowConfiguration.basements;
    for (let i = 0, l = rowContains.length; i < l; i++) {
      for (const j in obj.cells) {
        if (obj.cells[j].innerText === rowContains[i]) {
          return true;
        }
      }
    }
    return false;
  };
   // update and apply row configuration after get the row configuration
  const updateAndApplyRowConfig = function (obj) {
    const rowColor = rowConfiguration.coloringOption;
    const rowFont = rowConfiguration.fontOption;
    obj.find('td, th').each(function () {
      const childObj = $(this);
      let config = $(this).data('config') || {};
      if (!(childObj.attr('rowspan') > 1)) {
        if (rowColor) {
          config = updateConfig(config, 'color', rowColor);
        }
        if (rowFont) {
          config = updateConfig(config, 'fontWeight', rowFont);
        }
        $(this).data('config', config);
      }
      applyconfig($(this));
    });
  };


  table.append('thead').append('tr')
    .selectAll('th')
    .data(cols)
    .enter()
    .append('th')
    .text(function (d) {
      return d;
    });

  const filters = slice.getFilters();
  table.append('tbody')
    .selectAll('tr')
    .data(data.records)
    .enter()
    .append('tr')
    .selectAll('td')
    .data(row => data.columns.map((c) => {
      const val = row[c];
      let html;
      const isMetric = metrics.indexOf(c) >= 0;
      if (c === '__timestamp') {
        html = val;
      };
      if (c === fd.granularity_sqla){
          let new_val;
          if(typeof (val) === 'string'&& val.indexOf("-") === -1){
              new_val= new Date(val.substr(0,4), val.substr(4,2)-1, val.substr(6,2),0,0,0);
          }
          else{
              new_val=new Date(val);
          }
        html = tsFormatter(new_val.getTime())
      }
      else if (typeof (val) === 'string') {
          var reg =/^\d{4}-\d{2}-\d{2}T/;
          if(reg.test(val)){
              let new_val=new Date(val);
              html = tsFormatter(new_val.getTime())
          }
          else {
              html = `<span class="like-pre">${val}</span>`;
          }

      }
      if (isMetric) {
        const format_ = slice.datasource.column_formats[c] || fd.number_format || '.3s';
        html = d3format(format_, val);
      }
      return {
        col: c,
        val,
        html,
        isMetric,
      };
    }))
    .enter()
    .append('td')
    .style('background-image', function (d) {
      if (d.isMetric) {
        const r = (fd.color_pn && d.val < 0) ? 150 : 0;
        if (fd.align_pn) {
          const perc = Math.abs(Math.round((d.val / maxes[d.col]) * 100));
          // The 0.01 to 0.001 is a workaround for what appears to be a
          // CSS rendering bug on flat, transparent colors
          return (
            `linear-gradient(to right, rgba(${r},0,0,0.2), rgba(${r},0,0,0.2) ${perc}%, ` +
            `rgba(0,0,0,0.01) ${perc}%, rgba(0,0,0,0.001) 100%)`
          );
        }
        const posExtent = Math.abs(Math.max(maxes[d.col], 0));
        const negExtent = Math.abs(Math.min(mins[d.col], 0));
        const tot = posExtent + negExtent;
        const perc1 = Math.round((Math.min(negExtent + d.val, negExtent) / tot) * 100);
        const perc2 = Math.round((Math.abs(d.val) / tot) * 100);
        // The 0.01 to 0.001 is a workaround for what appears to be a
        // CSS rendering bug on flat, transparent colors
        return (
          `linear-gradient(to right, rgba(0,0,0,0.01), rgba(0,0,0,0.001) ${perc1}%, ` +
          `rgba(${r},0,0,0.2) ${perc1}%, rgba(${r},0,0,0.2) ${perc1 + perc2}%, ` +
          `rgba(0,0,0,0.01) ${perc1 + perc2}%, rgba(0,0,0,0.001) 100%)`
        );
      }
      return null;
    })
    .classed('text-right', d => d.isMetric)
    .attr('title', (d) => {
      if (!isNaN(d.val)) {
        return fC(d.val);
      }
      return null;
    })
    .attr('data-sort', function (d) {
      return (d.isMetric) ? d.val : null;
    })
    // Check if the dashboard currently has a filter for each row
    .classed('filtered', d =>
      filters &&
      filters[d.col] &&
      filters[d.col].indexOf(d.val) >= 0,
    )
    .on('click', function (d) {
      if (!d.isMetric && fd.table_filter) {
        const td = d3.select(this);
        if (td.classed('filtered')) {
          slice.removeFilter(d.col, [d.val]);
          d3.select(this).classed('filtered', false);
        } else {
          d3.select(this).classed('filtered', true);
          slice.addFilter(d.col, [d.val]);
        }
      }
    })
    .style('cursor', function (d) {
      return (!d.isMetric) ? 'pointer' : '';
    })
    .html(d => d.html ? d.html : d.val);
  const height = slice.height();
  let paging = false;
  let pageLength;
  if (fd.page_length && fd.page_length > 0) {
    paging = true;
    pageLength = parseInt(fd.page_length, 10);
  }
  slice.container.find('tbody tr').each(function () {
    $(this).find('td').each(function (i) {
      const metric = metricForCols[i];
      const format = slice.datasource.column_formats[metric] || fd.number_format || '.3s';
      const tdText = $(this)[0].textContent;
      $(this).attr('initialValue', tdText);
      if (!isNaN(tdText) && tdText !== '') {
        $(this)[0].textContent = d3format(format, tdText);
      }
    });
  });
    // apply row configuration
  function applyRowConfiguration() {
    if (rowConfiguration) {
      slice.container.find('tbody tr').each(function () {
        const hasRowConfig = getRowConfig(this);
        if (hasRowConfig) {
          updateAndApplyRowConfig($(this));
        }
      });
    }
  }
   // apply column configuration
  function applyColumnConfiguration() {
    if (columnConfiguration) {
      slice.container.find('tbody tr').each(function () {
        $(this).find('td').each(function (index) {
          const col = cols[index];
          const val = $(this).attr('initialValue') ||
            $(this).data('originalvalue') || $(this).text();
          $(this).data('originalvalue', val);
          const columnConfig = getColumnConfig(col);
          updateColumnConfig($(this), columnConfig, val);
          applyconfig($(this));
        });
      });
    }
  }
   if (rowConfigHasHighPriority) {
    applyColumnConfiguration();
    applyRowConfiguration();
  } else {
    applyRowConfiguration();
    applyColumnConfiguration();
  }
  const datatable = container.find('.dataTable').DataTable({
    paging,
    pageLength,
    aaSorting: [],
    searching: fd.include_search,
    bInfo: false,
    scrollY: height + 'px',
    scrollCollapse: true,
    scrollX: true,
    order: [],
  });
  fixDataTableBodyHeight(
      container.find('.dataTables_wrapper'), height);
  // Sorting table by main column
  // let sortBy;
  // if (fd.order_by_metric.length > 0) {
  //   // Sort by as specified
  //   sortBy = JSON.parse(fd.order_by_metric);
  // } else if (metrics.length > 0) {
  //   // If not specified, use the first metric from the list
  //   sortBy = [metrics[0], false];
  // } else if (fd.order_by_cols.length > 0) {
  //   sortBy = JSON.parse(fd.order_by_cols);
  // }
  // if (sortBy) {
  //   datatable.column(data.columns.indexOf(sortBy[0])).order(sortBy[1] ? 'asc' : 'desc');
  // }
  // if (fd.timeseries_limit_metric && metrics.indexOf(fd.timeseries_limit_metric) < 0) {
  //   // Hiding the sortBy column if not in the metrics list
  //   datatable.column(data.columns.indexOf(sortBy[0])).visible(false);
  // }
  datatable.draw();
  container.parents('.widget').find('.tooltip').remove();
}

module.exports = tableVis;
