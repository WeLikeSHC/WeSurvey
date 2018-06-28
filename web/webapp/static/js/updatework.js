/**
 * create by songjian on 2018/6/9.
 */


var host = document.getElementById("backend").value;


var sock = new SockJS("http://" + host + "/show_job");

var number = 0;

sock.onopen = function () {

    console.log('open');
    var name = document.getElementById("user_id").value;
    var request = {"user_id": name.toString ()};
    try {
        var requestToJson = JSON.stringify(request);  //将对象解析成json字符串
        sock.send(requestToJson);
    } catch (err) {
        alert("参数有错！");
    }
};

sock.onmessage = function (e) {
    var parse_info = JSON.parse(e.data);
    var status = false;
    if(parse_info['error'])
        return;
    var key = ['task_id', 'url', 'algorithm', 'number', 'dispersion', "cur_weight",
        'schedule', 'status', 'node_id', 'entry_time', 'result'];
    var trNode = document.getElementById("task" + parse_info['task_id']);
    if (trNode === null) {
        trNode = document.getElementById("task_body").insertRow();
        trNode.id = "task" + parse_info['task_id'];
        status = true;
    }
    for (var i = 0; i < key.length; i++) {
        if (status) {
            var tdNode = trNode.insertCell();
            tdNode.innerHTML = parse_info[key[i]];
        }
        else {
            try{
                trNode.cells[i].innerHTML = parse_info[key[i]];
            }
                catch (e) {
                console.log(e)
                console.log(parse_info[key[i]]);
                console.log(key[i]);

                }
            }
        if(status){
            document.getElementById("task_body").appendChild(trNode);
        }
        // document.getElementById("task_body").scrollTop = document.getElementById("task_body").scrollHeight;
    }

};

sock.onclose = function () {
    console.log('close');
};