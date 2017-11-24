import 'datatables.net';
import dt from 'datatables.net-bs';
import $ from 'jquery';
import 'datatables-bootstrap3-plugin/media/css/datatables-bootstrap3.css';

import { d3format, fixDataTableBodyHeight } from '../javascripts/modules/utils';
import './pivot_table.css';

dt(window, $);

module.exports = function (slice, payload) {
  const container = slice.container;
  const fd = slice.formData;
  const height = container.height();
  let cols = payload.data.columns;
  if (Array.isArray(cols[0])) {
    cols = cols.map(col => col[0]);
  }

  // payload data is a string of html with a single table element
  container.html(payload.data.html);

  // jQuery hack to set verbose names in headers
  const replaceCell = function () {
    const s = $(this)[0].textContent;
    $(this)[0].textContent = slice.datasource.verbose_map[s] || s;
  };
  slice.container.find('thead tr:first th').each(replaceCell);
  slice.container.find('thead tr:eq(1) th').each(replaceCell);
  slice.container.find('thead tr th:first-child').each(replaceCell);

  // jQuery hack to format number
  slice.container.find('tbody tr').each(function () {
    $(this).find('td').each(function (i) {
      const metric = cols[i];
      const format = slice.datasource.column_formats[metric] || fd.number_format || '.3s';
      const tdText = $(this)[0].textContent;
      if (!isNaN(tdText) && tdText !== '') {
        $(this)[0].textContent = d3format(format, tdText);
      }
    });
  });

  if (fd.groupby.length === 1) {
    // When there is only 1 group by column,
    // we use the DataTable plugin to make the header fixed.
    // The plugin takes care of the scrolling so we don't need
    // overflow: 'auto' on the table.
    container.css('overflow', 'hidden');
    const table = container.find('table').DataTable({
      paging: true,
      pageLength:50,
      aaSorting: [],
      searching: true,
      bInfo: true,
      scrollY: `${height}px`,
      scrollCollapse: true,
      aLengthMenu:[25,50,100,200,500,1000],
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
    fixDataTableBodyHeight(container.find('.dataTables_wrapper'), height-75);
    table.draw();
  } else {
    // When there is more than 1 group by column we just render the table, without using
    // the DataTable plugin, so we need to handle the scrolling ourselves.
    // In this case the header is not fixed.
    container.css('overflow', 'auto');
    container.css('height', `${height + 10}px`);
  }
};
