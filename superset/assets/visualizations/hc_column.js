import Highcharts from 'highcharts';
import {  getColor } from '../javascripts/modules/colors';
import $ from 'jquery';


function hc_column(slice, payload) {
    let f = 0; // 定义位于第几层，为了找到是第几层groupby
    let b = 0; // 定义位于第几层,为了找到sql语句是第几个
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
    let next_type = 'column';
    let query_sql = [payload.query];
    let dafaultMenuItem = Highcharts.getOptions().exporting.buttons.contextButton.menuItems;
    const chart = {
        subtitle: {
            text: 'Drill down histogram'
        },
        chart: {
            type: 'column',
            events: {
                drillup: function (e) {
                    // 上钻回调事件
                    f -= 1;
                    query_sql.pop();
                    b -= 1;
                },
                drilldown: function (e) {
                    // 下钻事件
                    if (!e.seriesOptions) {
                        var chart = this;
                        chart.showLoading('正在加载数据 ...');
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
                            data: {form_data: JSON.stringify(formdata)}, // 构建form表单
                            timeout: 15000,
                            success: function (data) {
                                const drill_down_data = [];
                                data.data.data.forEach(function (item) {
                                    item.drilldown = data.data.drill_down;
                                    drill_down_data.push(item);
                                });
                                query_sql.push(data.query); // sql语句
                                b += 1;
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
        exporting: {
            buttons: {
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
                            // 显示查询语句模态框
                            onclick: function () {
                                function commitResult() { // 要出发的函数
                                    this.parentNode.parentNode.parentNode.style.display = "none"; //这里时为了获得 modal_bc;
                                }

                                create_modal(false, query_sql, commitResult);

                                function create_modal(alert_or_confirm, modal_contents, confirm_trigger_function) {
                                    let modal_bg = document.createElement("div");
                                    let modal_container = document.createElement("div");

                                    let modal_title = document.createElement("div");
                                    let modal_content = document.createElement("div");
                                    let modal_little_content = document.createElement("pre");
                                    let modal_copy_btn = document.createElement('button');
                                    //设置id
                                    modal_bg.setAttribute("id", "modal_bg");
                                    modal_container.setAttribute("id", "modal_container");
                                    modal_title.setAttribute("id", "modal_title");
                                    modal_content.setAttribute("id", "modal_content");
                                    modal_little_content.setAttribute("id", "modal_little_content");
                                    modal_copy_btn.setAttribute("id", "copy");
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
                                        "font-weight: 300;" +
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
                                    modal_copy_btn.style.cssText =
                                        "border-width: 0px;" + /* 边框宽度 */
                                        "border-radius: 3px;" + /* 边框半径 */
                                        "cursor: pointer;" + /* 鼠标移入按钮范围时出现手势 */
                                        "font-family: Microsoft YaHei;" + /* 设置字体 */

                                    modal_container.appendChild(modal_title);
                                    modal_container.appendChild(modal_content);
                                    modal_content.appendChild(modal_copy_btn);
                                    modal_content.appendChild(modal_little_content);
                                    modal_bg.appendChild(modal_container);
                                    //将整个模态框添加到body中
                                    document.body.appendChild(modal_bg);

                                    //给模态框添加相应的内容
                                    modal_copy_btn.innerHTML = "复制";
                                    modal_title.innerHTML = "查询语句";
                                    modal_little_content.innerHTML = modal_contents[b];

                                    //复制按钮
                                    modal_copy_btn.addEventListener('click',() => {
                                        const input = document.createElement('input');
                                        document.body.appendChild(input);
                                        input.setAttribute('value', modal_contents[b]);
                                        input.select();
                                        if (document.execCommand('copy')) {
                                            document.execCommand('copy');
                                        }
                                        document.body.removeChild(input);
                                    });

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
            // 改变x轴刻度
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
        // 是否显示图例
        legend: {
            enabled: fd.show_legend,
        },
        // 格式化显示信息
        tooltip: {
            formatter: function() {
            return '<b>'+ this.point.name +'</b>: ' +'('+
                         Highcharts.numberFormat(this.y, 0, ',') +' )';
         }
                    },
        // 更改颜色
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