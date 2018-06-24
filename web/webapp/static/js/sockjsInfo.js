/**
 * create by songjian on 2018/6/9.
 */


var host = document.getElementById("backend").value;


var sock = new SockJS("http://" + host + "/show_js");

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
    var name = document.getElementById("node_name").value;
    var request = {"node_name": name.toString()};
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

        memory = Highcharts.chart('memory', {
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
                text: '结点' + parse_info[0]['name'] + " 内存使用率变化图"
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
                    text: '内存使用率'
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
                name: '当前内存使用率',
                data: (function () {
                    var data = [], i;
                    for (i = 0; i < parse_info.length; i += 1) {
                        data.push({
                            x: new Date(parse_info[i]['time']).getTime(),
                            y: parse_info[i]['memory_use']
                        });
                    }
                    return data;
                }())
            }]
        });

        cpu = Highcharts.chart('cpu', {
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
                text: '结点' + parse_info[0]['name'] + " CPU使用率变化图"
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
                    text: 'CPU使用率'
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
                name: '当前CPU使用率',
                data: (function () {
                    var data = [], i;
                    for (i = 0; i < parse_info.length; i += 1) {
                        data.push({
                            x: new Date(parse_info[i]['time']).getTime(),
                            y: parse_info[i]['cpu_use']
                        });
                    }
                    return data;
                }())
            }]
        });
    }
    else {
        memory.series[0].addPoint([new Date(parse_info['time']).getTime(), parse_info["memory_use"]], true, true);
        activeLastPointToolip(memory);
        cpu.series[0].addPoint([new Date(parse_info['time']).getTime(), parse_info["cpu_use"]], true, true);
        activeLastPointToolip(cpu);
        for(var temp in parse_info){
            if(temp !== "time" && temp!== "name"){
                try{
                    document.getElementById(temp).value = parse_info[temp];
                }
                catch (e) {
                    console.log(temp);
                }
            }

        }
    }
};

sock.onclose = function () {
    console.log('close');
};

