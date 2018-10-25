
import drilldown from 'highcharts/modules/drilldown.js';
import Highcharts from 'highcharts';
import $ from 'jquery';
drilldown(Highcharts);

function hc_pie(slice, payload) {
    const div = d3.select(slice.selector);
    console.log('slice', slice.selector);
    console.log('payload',payload);
    const sliceId = 'hc_pie_slice_' + slice.formData.slice_id;
    const html = '<div id=' + sliceId + ' style="width:' + slice.width() + 'px;height:' + slice.height() + 'px;"></div>';
    div.html(html); // reset

    // const myChart = Highcharts.init(document.getElementById(sliceId));

    const fd = slice.formData;
    const json = payload.data;
    console.log(payload.data);
    if(json.drilldown){
        console.log(1111);
        json.data.forEach(function (item) {
            item.drilldown = true
        })
    }else{
        console.log(222);
    }

    // const dataName = [];  // echarts需要的是两个数组
    // let maxValue = 0;
    // const dataValue = json;
    // dataValue.forEach(function (item) {
    // dataName.push(item.name);
    // if (item.value > maxValue) {
    //     maxValue = item.value;
    //     }
    // });
    const chart = {
        chart: {
            type  : 'pie',
            events: {
              drillup: function(e) {
                // 上钻回调事件
                console.log(e.seriesOptions);
              },
              drilldown: function (e) {
                if (!e.seriesOptions) {
                  var chart      = this,
                      drilldowns = {
                      'Animals': {
                        name: 'Animals',
                        data: [
                          {name:'Cows',
                           y        : 2,
                           drilldown: true
                          },
                        ]
                      },
                      'Fruits': {
                        name: 'Fruits',
                        data: [
                          ['Apples', 5],
                          ['Oranges', 7],
                          ['Bananas', 2]
                        ]
                      },
                      'Cars': {
                        name: 'Cars',
                        data: [
                          ['Toyota', 1],
                          ['Volkswagen', 2],
                          ['Opel', 5]
                        ]
                      },
                      'Cows':{
                        name: 'Cows',
                        data: [
                          ['big', 2],
                          ['small', 3]
                        ]},
                    },
                    series = drilldowns[e.point.name];
                  // Show the loading label
                  chart.showLoading('Simulating Ajax ...');
                  setTimeout(function () {
                    chart.hideLoading();
                    chart.addSeriesAsDrilldown(e.point, series);
                  }, 1000);
                }
              }
            }
          },
          title: {
            text: 'Async drilldown'
          },
          xAxis: {
            type: 'category'
          },
          legend: {
            enabled: false
          },
          plotOptions: {
            series: {
              borderWidth: 0,
              dataLabels : {
                enabled: true
              }
            }
          },
          series: [{
            name        : 'test',
            colorByPoint: true,
            data        : [{
              name     : 'Animals',
              y        : 5,
              drilldown: true
            }, {
              name     : 'Fruits',
              y        : 2,
              drilldown: true
            }, {
              name     : 'Cars',
              y        : 4,
              drilldown: true
            }]
          }],
          drilldown: {
            series: []
          }
    };
    Highcharts.chart(document.getElementById(sliceId),chart);
}
module.exports = hc_pie;
