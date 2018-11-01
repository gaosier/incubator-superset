import Highcharts from 'highcharts';
import {  getColor } from '../javascripts/modules/colors';
import $ from 'jquery';


function hc_column(slice, payload) {
    console.log(slice.formData);
    let f = 0;
    const div = d3.select(slice.selector);
    const sliceId = 'hc_column_slice_' + slice.formData.slice_id;
    const html = '<div id=' + sliceId + ' style="width:' + slice.width() + 'px;height:' + slice.height() + 'px;"></div>';
    div.html(html); // reset
    const fd = slice.formData;
    const json = payload.data;
    const colorlist = getColor(fd.color_scheme);
    const data = [];
    json.data.forEach(function (item) {
        item.drilldown = json.drill_down;
        data.push(item);
    });
    const chart = {
        chart: {
            type: 'column',
            events: {
                drillup: function (e) {
                    // 上钻回调事件
                    f -= 1;
                },
                drilldown: function (e) {
                    if (!e.seriesOptions) {
                        var chart = this;
                        chart.showLoading('Simulating Ajax ...');
                        const formdata = fd;
                        const val = e.point.name.split('/');
                        formdata["extra_filters"] = [{
                            "col": formdata.groupby[f],
                            "op": "==",
                            "val": val[val.length - 1]
                        }];
                        f += 1;

                        $.ajax({
                            url: encodeURI("/superset/explore_json/?form_data={\"slice_id\"\:" + formdata.slice_id + "}"),
                            type: "POST",
                            data: {form_data: JSON.stringify(formdata)},
                            timeout: 2000,
                            success: function (data) {
                                const drill_down_data = [];
                                data.data.data.forEach(function (item) {
                                    item.drilldown = data.data.drill_down;
                                    drill_down_data.push(item);
                                });
                                const drill_down = {
                                    name: 'value',
                                    data: drill_down_data
                                };
                                const series = drill_down;
                                chart.hideLoading();
                                chart.addSeriesAsDrilldown(e.point, series);
                            },
                            error: function (xhr, status, err) {
                            },
                        });
                    }
                }
            }
        },
        title: {
            text: ''
        },
        xAxis: {
            type: 'category',
            title:{
                text:fd.x_axis_label
                }
        },
        yAxis:{
            title:{
                text:fd.y_axis_label
            },
            labels:{
                formatter:function(){
                    if(fd.y_axis_format ==='.'){
                        return this.value
                    }else if(fd.y_axis_format === '.1s'){
                        return (this.value/1000).toFixed(0) + 'K';
                    }else if(fd.y_axis_format === '.3s'){
                        return (this.value/1000).toFixed(2) + 'K';
                    }else if(fd.y_axis_format === '.1%'){
                        return (this.value*10).toFixed(1) + '%';
                    }else if(fd.y_axis_format === '.3%'){
                        return (this.value*10).toFixed(3) + '%';
                    }else if(fd.y_axis_format === '.3f'){
                        return (this.value).toFixed(3);
                    }else if(fd.y_axis_format === '+,'){
                        return '+' + Number(this.value).toLocaleString()
                    }else{
                        return this.value
                    }
            }
            }
        },
        legend: {
            enabled: fd.show_legend,
        },
        tooltip: {
            formatter: function() {
            return '<b>'+ this.point.name +'</b>: ' +'('+
                         Highcharts.numberFormat(this.y, 0, ',') +' )';
         }
                    },
        colors :colorlist,
        plotOptions: {
            series: {
                borderWidth: 0,
                dataLabels: {
                    enabled: true
                }
            }
        },
        credits:{
            enabled: false // 禁用版权信息
        },
        series: [{
            name: 'value',
            colorByPoint: true,
            data: data,
        }]

    };
    Highcharts.chart(document.getElementById(sliceId), chart);

}

module.exports = hc_column;