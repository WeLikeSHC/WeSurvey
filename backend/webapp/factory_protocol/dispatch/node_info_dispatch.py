# coding=utf-8

from job_dispatch import NodeDisPatch
import json
import time

"""
node 结点协议

当创建连接时, 传递结点的参数 包括 id 和 权值 id 为结点名称, 结点所在rpc服务器地址

{'id':'slave1', 'weight': 20, 'rpc_address':"127.0.0.1:5003"}

当非第一次连接时，发送的是实时的消息 更新任务的实时状态
格式如:

更新某个任务的状态

json 格式中 status 为信息状态 表示这条信息是否正常 正常为 200 异常为 500

id 为slave结点的id号

task_id 为 任务的编号

entry_time 为更新时间

task_status 为任务状态

schedule 为任务进度

{'status':200, 'id': 1 ,'task_id':'1', 'entry_time':'2017-2-2', 'task_status':'working', 'schedule':0.02}

某个任务成功
{'status':200, 'id': 1, 'task_id':'1', 'entry_time':'2017-2-2', 'task_status':'finish', 'schedule':1}

某个任务失败

{'status':200, 'id': 1, 'task_id':'1', 'entry_time':'2017-2-2', 'task_status':'failed', 'schedule':1}

发送异常信息

{'status':500, 'id': 1, 'info':"error info"}

"""


class TaskDispatch:

    def __init__(self):
        self.error_info = [u"<a>生成失败</a>", u"<a>超过最大重试次数</a>", u"<a>no slave</a>", u"<a>任务超时</a>"]
        self.normal_info = [u'<a>正在生成</a>']

    def dispatch(self, task):
        result = self.info_check(task)
        if not result:
            NodeDisPatch.work[task.get('task_id')] = task
            # db.execute_insert('sensor', temp.keys(), [temp[key] for key in temp.keys()])
            for observe in self.factory.OnlineProtocol.observe.get('user' + task['user_id']):
                # 观察者模式　发送给所有关注该结点的sockjs
                observe.transport.write(json.dumps(task))
        return result

    def info_check(self, info):
        try:
            info = json.loads(info)
            _time = info['entry_time']
            time_list = time.strptime(_time, '%Y-%m-%d %H:%M:%S')
            total = time.mktime(time_list)
            cur = int(time.time())
            node_list = self.factory.OnlineProtocol.get_online_protocols("node")
            task_id = NodeDisPatch.work.get(info.get('task_id'))
        except Exception as e:
            return {"status": 501, "info": str(e)}

        if not task_id:
            return {"status": 404, "info": "task_id not find"}

        if cur - total > 20:
            return {"status": 501, "info": u"时间超时，无效信息! 提交时间为{} , "
                                           u"更新时间为{}".format(NodeDisPatch.work[task_id['task_id']]['entry_time'], _time)}
        if info['status'] == "work" and info['result'] not in self.normal_info:
            return {"status": 501, "info": u"当前状态是 work 但是状态为 {}".format(info['result'])}

        if info['status'] == 'failed' and info['result'] not in self.error_info:
            return {"status": 501, "info": u"当前状态是 failed 但是状态为 {}".format(info['result'])}

        if info['status'] == "finish" and u"点击下载" not in info['result']:
            return {"status": 501, "info": u"当前状态是 finish 但是状态为 {}".format(info['result'])}

        if node_list and info['result'] == "<a>no slave</a>":
            return {"status": 501, "info": u"当前存在结点 但是状态为 {}".format(info['result'])}

        return {}


TaskDispatch = TaskDispatch()
