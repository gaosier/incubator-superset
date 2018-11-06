import Highcharts from 'highcharts';
import drilldown from 'highcharts/modules/drilldown.js';
import {getColor} from '../javascripts/modules/colors';
import $ from 'jquery';
import exporting from 'highcharts/modules/exporting';
import 'highcharts/modules/exporting.src';

drilldown(Highcharts);
exporting(Highcharts);

Highcharts.setOptions({
    lang: {
        drillUpText: "返回上一级",
        loading: "加载中",
        contextButtonTitle: "图表导出菜单",
        downloadJPEG: "下载 JPEG 图片",
        downloadPDF: "下载 PDF 文件",
        downloadPNG: "下载 PNG 文件",
        downloadSVG: "下载 SVG 文件",
        printChart: "打印图表"
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
    const colorlist = getColor(fd.color_scheme);
    const data = [];
    json.data.forEach(function (item) {
        item.drilldown = json.drill_down;
        data.push(item);
    });
    let next_type = 'pie';
    let dafaultMenuItem = Highcharts.getOptions().exporting.buttons.contextButton.menuItems;
    const chart = {
        subtitle: {
            text: 'The tooltip should provide a HTML table where the table is closed in the footerFormat'
        },
        exporting: {
            buttons: {
                exportButton: {
                    y: 0 //默认是10
                },
                printButton: {
                    y: 0
                },
                contextButton: {
                    // 自定义导出菜单项目及顺序
                    menuItems: [
                        dafaultMenuItem[0],
                        {
                            separator: true
                        },
                        dafaultMenuItem[3],
                        {
                            text: '下载 PDF 文件',
                            onclick: function () {
                                this.exportChart({
                                    type: 'application/pdf'
                                });
                            }
                        },
                        {
                            text: '下钻类型改为饼图',
                            onclick: function () {
                                next_type = 'pie';

                            }
                        },
                        {
                            text: '下钻类型改为柱状图',
                            onclick: function () {
                                next_type = 'column';

                            }
                        },
                        {
                            text: '下钻类型改为折线图',
                            onclick: function () {
                                next_type = 'spline';

                            }
                        },
                        dafaultMenuItem[5],
                        dafaultMenuItem[1],
                        {
                            text: '查询语句',
                            onclick: function () {
                                function commitResult() { // 要出发的函数
                                    this.parentNode.parentNode.parentNode.style.display = "none"; //这里时为了获得 modal_bc;
                                }

                                create_modal(false, "你确定要提交该单词么", commitResult);

                                function create_modal(alert_or_confirm, modal_contents, confirm_trigger_function) {
                                    let modal_bg = document.createElement("div");
                                    let modal_container = document.createElement("div");

                                    let modal_title = document.createElement("div");
                                    let modal_content = document.createElement("div");
                                    let modal_little_content = document.createElement("div");
                                    //设置id
                                    modal_bg.setAttribute("id", "modal_bg");
                                    modal_container.setAttribute("id", "modal_container");
                                    modal_title.setAttribute("id", "modal_title");
                                    modal_content.setAttribute("id", "modal_content");
                                    modal_little_content.setAttribute("id", "modal_little_content");
                                    //设置样式
                                    modal_bg.style.cssText = "display:block;" +
                                        "background-color: rgba(0,0,0,0.4);" +
                                        "position:fixed;" +
                                        "top:0;" +
                                        "bottom:0;" +
                                        "right:0;" +
                                        "left:0;";
                                    modal_container.style.cssText = "background-color:white;" +
                                        "width:500px;" +
                                        "height:260px;" +
                                        "margin:10% auto;";
                                    modal_title.style.cssText = "color:black;" +
                                        "font-family: Helvetica, Arial;" +
                                        "font-weight: 300;"+
                                        "text-align:center;" +
                                        "font-size: 18px;" +
                                        "width:100%;" +
                                        "height:50px;" +
                                        "color: inherit;" +
                                        "line-height:50px;";
                                    modal_content.style.cssText = "color:black;" +
                                        "width:100%;" +
                                        "height:210px;" +
                                        "border-bottom:2px solid grey";
                                    modal_little_content.style.cssText = "padding:14px 15px 15px 15px;" +
                                        "background-color: #F5F5F5;" +
                                        "color:black;" +
                                        "width:500px;" +
                                        "height:210px;";


                                    modal_container.appendChild(modal_title);
                                    modal_container.appendChild(modal_content);
                                    modal_content.appendChild(modal_little_content);
                                    // modal_container.appendChild(modal_footer);
                                    modal_bg.appendChild(modal_container);
                                    //将整个模态框添加到body中
                                    document.body.appendChild(modal_bg);

                                    //给模态框添加相应的内容
                                    modal_title.innerHTML = "聚合查询";
                                    modal_little_content.innerHTML = modal_contents;
                                    // modal_footer.innerHTML = "This is a modal footer";

                                    // 制作关闭按钮
                                    let close_button = document.createElement("span");
                                    close_button.innerHTML = "&times;";
                                    close_button.setAttribute("id", "modal_close_button");
                                    close_button.style.cssText = " margin-right:8px;" +
                                        "line-height:50px;" +
                                        "color: #aaa;" +
                                        "float: right;" +
                                        "font-size: 28px;" +
                                        "font-weight: bold;";
                                    close_button.onmouseover = function (event) {
                                        close_button.style.color = "black";
                                        event = event || window.event;
                                        event.stopPropagation();
                                    };
                                    document.onmouseover = function () {
                                        document.getElementById("modal_close_button").style.color = "#aaa";
                                    };
                                    close_button.addEventListener("click", function () {
                                        modal_bg.style.display = "none"
                                    });
                                    modal_title.appendChild(close_button);

                                }

                            }
                        }
                    ]
                }
            }
        },
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
                        chart.showLoading('正在加载数据 ...');
                        const formdata = fd;
                        const val = e.point.name.split('/');
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
                            timeout: 15000,
                            success: function (data) {
                                console.log(data);
                                const drill_down_data = [];
                                data.data.data.forEach(function (item) {
                                    item.drilldown = data.data.drill_down;
                                    drill_down_data.push(item);
                                });
                                const drill_down = {
                                    name: 'value',
                                    type: next_type,
                                    data: drill_down_data
                                };
                                const series = drill_down;
                                chart.hideLoading();
                                chart.addSeriesAsDrilldown(e.point, series);
                            },
                            error: function (xhr, status, err) {
                                alert('数据获取失败,请重试');
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
                return this.name + '(' + Highcharts.numberFormat(this.percentage, 2) + '%)' + '(' + Highcharts.numberFormat(this.y, 0, ',') + ')';//在名称后面追加百分比数据
            }

        },
        tooltip: {
            formatter: function () {
                return '<b>' + this.point.name + '</b>: ' + Highcharts.numberFormat(this.percentage, 2) + '% (' +
                    Highcharts.numberFormat(this.y, 0, ',') + ' )';
            }
        },
        colors: colorlist,
        plotOptions: {
            pie: {
                allowPointSelect: false, //选中某块区域是否允许分离
                cursor: 'pointer',
                dataLabels: {
                    enabled: true, //是否直接呈现数据 也就是外围显示数据与否
                    distance: fd.labels_outside ? 20 : -70,
                    formatter: function () {
                        if (fd.pie_label_type === 'value') {
                            return this.y;
                        } else if (fd.pie_label_type === 'percent') {
                            return Highcharts.numberFormat(this.percentage, 2) + '%'
                        } else if (fd.pie_label_type === 'key') {
                            return this.point.name
                        } else if (fd.pie_label_type === 'key_value') {
                            return this.point.name + '(' + this.y + ')'
                        } else if (fd.pie_label_type === 'key_percent') {
                            return this.point.name + Highcharts.numberFormat(this.percentage, 2) + '%';
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
        credits: {
            enabled: false // 禁用版权信息
        },
        series: [{
            name: 'value',
            colorByPoint: true,
            data: data,
            innerSize: fd.donut ? '50%' : '0%'
        }]

    };
    Highcharts.chart(document.getElementById(sliceId), chart);

}

module.exports = hc_pie;