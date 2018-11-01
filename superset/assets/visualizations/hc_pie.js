import drilldown from 'highcharts/modules/drilldown.js';
import Highcharts from 'highcharts';
import {  getColor } from '../javascripts/modules/colors';
import $ from 'jquery';

drilldown(Highcharts);

Highcharts.setOptions({
	lang:{
		drillUpText:"返回上一级",
		loading:"加载中",
	}
});
function hc_pie(slice, payload) {
    let a = 0;
    const div = d3.select(slice.selector);
    const sliceId = 'hc_pie_slice_' + slice.formData.slice_id;
    const html = '<div id=' + sliceId + ' style="width:' + slice.width() + 'px;height:' + slice.height() + 'px;"></div>';
    div.html(html); // reset
    const fd = slice.formData;
    const json = payload.data;
    // if(fd.labels_outside){
    //     let b = 20;
    // }else{
    //     let b = -70;
    // }
    // if(fd.donut){
    //     let c = '50%';
    // }else{
    //     let c = '0%';
    // }
    const colorlist = getColor(fd.color_scheme);
    const data = [];
    json.data.forEach(function (item) {
        item.drilldown = json.drill_down;
        data.push(item);
    });
    const chart = {
        chart: {
            type: 'pie',
            events: {
                drillup: function (e) {
                    // 上钻回调事件
                    a -= 1;
                },
                drilldown: function (e) {
                    if (!e.seriesOptions) {
                        var chart = this;
                        chart.showLoading('Simulating Ajax ...');
                        const formdata = fd;
                        const val = e.point.name.split('/');
                        console.log(formdata.groupby);
                        formdata["extra_filters"] = [{
                            "col": formdata.groupby[a],
                            "op": "==",
                            "val": val[val.length - 1]
                        }];
                        a += 1;

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
            type: 'category'
        },
        legend: {
            enabled: true,
            labelFormatter: function () {
                            return this.name + '('+Highcharts.numberFormat(this.percentage, 2)+'%)' + '('+Highcharts.numberFormat(this.y, 0, ',')+')';//在名称后面追加百分比数据
                        }

        },
        tooltip: {
            formatter: function() {
            return '<b>'+ this.point.name +'</b>: '+ Highcharts.numberFormat(this.percentage, 2) +'% ('+
                         Highcharts.numberFormat(this.y, 0, ',') +' )';
         }
                    },
        colors :colorlist,
        plotOptions: {
            pie: {
                allowPointSelect: true, //选中某块区域是否允许分离
                cursor: 'pointer',
                dataLabels: {
                    enabled: true, //是否直接呈现数据 也就是外围显示数据与否
                    distance: fd.labels_outside?20:-70,
                    formatter: function() {
                        if(fd.pie_label_type==='value'){
                            return   this.y;
                        }else if(fd.pie_label_type==='percent'){
                            return Highcharts.numberFormat(this.percentage, 2) + '%'
                        }else if(fd.pie_label_type==='key'){
                            return this.point.name
                        }else if(fd.pie_label_type==='key_value'){
                            return this.point.name + '(' +this.y + ')'
                        }else if(fd.pie_label_type==='key_percent'){
                            return  this.point.name + Highcharts.numberFormat(this.percentage, 2) + '%';
                        }

      },
                },
                showInLegend: fd.show_legend
            },

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
            innerSize: fd.donut?'50%':'0%'
        }]

    };
    Highcharts.chart(document.getElementById(sliceId), chart);

}

module.exports = hc_pie;