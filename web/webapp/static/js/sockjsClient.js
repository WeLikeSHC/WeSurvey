/**
 * create by songjian on 2018/6/9.
 */


var host = document.getElementById("backend").value;

type_list = {'temp': '温度', 'mois': '湿度'};

var sock = new SockJS("http://" + host + "/show_data");

var number = 0;

Highcharts.setOptions({
    global: {
        useUTC: false
    }
});

function activeLastPointToolip(chart) {
    var points = chart.series[0].points;
    chart.tooltip.refresh(points[points.length - 1]);
}


sock.onopen = function () {

    console.log('open');
    var name = document.getElementById("sensor").value;
    var request = {"sensor_name": name.toString()};
    try {
        var requestToJson = JSON.stringify(request);  //将对象解析成json字符串
        sock.send(requestToJson);
    } catch (err) {
        alert("参数有错！");
    }
};

function insertTable(tbody_id, info_list) {
    var node_table = document.getElementById(tbody_id);
    if (node_table) {
        /*
        *               <th>结点ID</th>
                        <th>结点名称</th>
                        <th>结点类型</th>
                        <th>结点数据</th>
                        <th>测量时间</th>
        * */
        var trNode = node_table.insertRow();

        var list = {0: "id", 1: "name", 2: "type", 3: "entry_data", 4: "entry_time"};
        for (var i = 0; i < 5; i++) {
            var tdNode = trNode.insertCell();
            tdNode.innerText = info_list[list[i]];
            tdNode.id = "td" + number;
            number += 1;
            // document.getElementById(tdNode.id).scrollIntoView(true);
            node_table.scrollTop = node_table.scrollHeight;
        }
        node_table.appendChild(trNode);
    }
}

sock.onmessage = function (e) {
    var parse_info = JSON.parse(e.data);
    if (parse_info instanceof Array) {
        chart = Highcharts.chart('container', {
            chart: {
                type: 'spline',
                marginRight: 10,
                events: {
                    load: function () {
                        var series = this.series[0],
                            chart = this;
                        activeLastPointToolip(chart);
                    }
                }
            },
            title: {
                text: '物联网采集结点: ' + parse_info[0]['name'] + ' 数据显示曲线图 类型 (' + type_list[parse_info[0]['type']] + ')'
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150,
                title: {
                    text: "时间"
                }
            },
            yAxis: {
                title: {
                    text: type_list[parse_info[0]['type']]
                }
            },
            tooltip: {
                formatter: function () {
                    return '<b>' + this.series.name + '</b><br/>' +
                        Highcharts.dateFormat('%Y-%m-%d %H:%M:%S', this.x) + '<br/>' +
                        Highcharts.numberFormat(this.y, 2);
                }
            },
            legend: {
                enabled: false
            },
            series: [{
                name: '实时' + type_list[parse_info[0]['type']],
                data: (function () {
                    var data = [], i;
                    for (i = 0; i < parse_info.length; i += 1) {
                        data.push({
                            x: new Date(parse_info[i]['entry_time']).getTime(),
                            y: parse_info[i]['entry_data']
                        });
                    }
                    return data;
                }())
            }]
        });

        for(var j=0;j<parse_info.length;j++)
            insertTable('tbody_id', parse_info[j]);
    }
    else {
        chart.series[0].addPoint([new Date(parse_info['entry_time']).getTime(), parse_info["entry_data"]], true, true);
        activeLastPointToolip(chart);
        insertTable('tbody_id', parse_info);

    }
};

sock.onclose = function () {
    console.log('close');
};

