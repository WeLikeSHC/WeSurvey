/**
 * create by songjian on 2018/6/9.
 */


var host = document.getElementById("backend").value;
console.log(host, name);

var sock = new SockJS("http://" + host + "/show_data");

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
                text: '动态模拟实时数据'
            },
            xAxis: {
                type: 'datetime',
                tickPixelInterval: 150
            },
            yAxis: {
                title: {
                    text: null
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
                name: 'Random data',
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
    }
    else {
        console.log(parse_info["entry_data"])
        chart.series[0].addPoint([new Date(parse_info['entry_time']).getTime(), parse_info["entry_data"]], true, true);
        activeLastPointToolip(chart);

    }
};

sock.onclose = function () {
    console.log('close')
};

