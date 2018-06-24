/**
 * create by songjian on 2018/6/9.
 */


var host = document.getElementById("backend").value;


var sock = new SockJS("http://" + host + "/show_job");

var number = 0;

sock.onopen = function () {

    console.log('open');
    var name = document.getElementById("user_id").value;
    var request = {"user_id": name.toString()};
    try {
        var requestToJson = JSON.stringify(request);  //将对象解析成json字符串
        sock.send(requestToJson);
    } catch (err) {
        alert("参数有错！");
    }
};

sock.onmessage = function (e) {
    var parse_info = JSON.parse(e.data);
    var trNode = document.getElementById("task" + parse_info['task_id']);
    var key = ['task_id', 'url', 'algorithm', 'number', 'dispersion', 'schedule', 'status', 'node_id', 'entry_time'];
        for(var i=0;i< trNode.cells.length - 1; i++){
            if(key[i] === 'cur_weight')
                continue;
            trNode.cells[i].innerHTML = parse_info[key[i]];
    }
};

sock.onclose = function () {
    console.log('close');
};