import d3 from 'd3';
// import 'datatables-bootstrap3-plugin/media/css/datatables-bootstrap3.css';
import 'datatables.net-bs/css/dataTables.bootstrap.css';
import 'datatables.net';
import dt from 'datatables.net-bs';

import { fixDataTableBodyHeight, d3TimeFormatPreset ,d3format} from '../javascripts/modules/utils';
import './table.css';

const $ = require('jquery');

dt(window, $);

function tableVis(slice, payload) {
  const container = $(slice.selector);
  const fC = d3.format('0,000');

  const data = payload.data;
  const fd = slice.formData;

  // Removing metrics (aggregates) that are strings
  let metrics = fd.metrics || [];
  metrics = metrics.filter(m => !isNaN(data.records[0][m]));

  function col(c) {
    const arr = [];
    for (let i = 0; i < data.records.length; i += 1) {
      arr.push(data.records[i][c]);
    }
    return arr;
  }
  const maxes = {};
  for (let i = 0; i < metrics.length; i += 1) {
    maxes[metrics[i]] = d3.max(col(metrics[i]));
  }

  const tsFormatter = d3TimeFormatPreset(fd.table_timestamp_format);

  const div = d3.select(slice.selector);
  div.html('');
  const table = div.append('table')
    .classed(
      'dataframe dataframe table table-striped table-bordered ' +
      'table-condensed table-hover dataTable no-footer', true)
    .attr('width', '100%');

  const cols = data.columns.map(c => slice.datasource.verbose_map[c] || c);

  table.append('thead').append('tr')
    .selectAll('th')
    .data(cols)
    .enter()
    .append('th')
    .text(function (d) {
      if (d === '__timestamp') {
          return '时间分组';
      }
      else
          return d;
    })
    .style('min-width', function (d) {
           let le = d.replace(/[\u0391-\uFFE5]/g,"aa").length;
           let c = parseInt(le/5);
           if(c == 2){
                return c*12 + 'px';
           }else if(c == 3){
                return c*12 + 'px';
           }else if(c > 3){
                return '48px'
           }
           else{
            return null;
           }
    });

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
        const perc = Math.round((d.val / maxes[d.col]) * 100);
        // The 0.01 to 0.001 is a workaround for what appears to be a
        // CSS rendering bug on flat, transparent colors
        return (
          `linear-gradient(to left, rgba(0,0,0,0.2), rgba(0,0,0,0.2) ${perc}%, ` +
          `rgba(0,0,0,0.01) ${perc}%, rgba(0,0,0,0.001) 100%)`
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
    .style('min-width', function (d) {
           let v= d.val;
           if(!v){
            return null;
           }
           v = v + '';
           let le = v.replace(/[\u0391-\uFFE5]/g,"aa").length;
           let c = parseInt(le/10);
           if(c == 2){
            return  '120px';
           }else if(c==3){
            return '160px'
           }else if(c>3){
            return '200px'
           }
           else{
            return null;
           }
    })
    .html(d => d.html ? d.html : d.val);
  const height = slice.height();
  let paging = false;
  let pageLength;
  if (fd.page_length && fd.page_length > 0) {
    paging = true;
    pageLength = parseInt(fd.page_length, 10);
  }
  const datatable = container.find('.dataTable').DataTable({
    paging,
    pageLength,
    aaSorting: [],
    searching: fd.include_search,
    bInfo: true,
    scrollY: height,
    scrollCollapse: true,
    aLengthMenu:[10,25,40,50,75,100,150,200],
    scrollX: true,
    bPaginate : true,
    oLanguage: {
        sLengthMenu: "每页显示 _MENU_ 条记录",
        sZeroRecords: "抱歉， 没有找到",
        // sInfo: "从 _START_ 到 _END_ /共 _TOTAL_ 条数据",
        sInfo: "总共_PAGES_ 页，显示第_START_ 到第 _END_ ，筛选之后得到 _TOTAL_ 条",
        sInfoEmpty: "没有数据",
        sInfoFiltered: "(从 _MAX_ 条数据中检索)",
        oPaginate: {
            sFirst: "首页",
            sPrevious: "前一页",
            sNext: "后一页",
            sLast: "尾页"
        },
        sSearch: '<span class="label label-success">搜索：</span>'}
  });
  fixDataTableBodyHeight(
      container.find('.dataTables_wrapper'), height-75);
  // Sorting table by main column
  if (metrics.length > 0) {
    const mainMetric = metrics[0];
    // datatable.column(data.columns.indexOf(mainMetric)).order('desc').draw();
    datatable.draw();
  }
  container.parents('.widget').find('.tooltip').remove();
}

module.exports = tableVis;
