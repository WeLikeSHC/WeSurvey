# coding=utf-8

import json
from twisted.internet.protocol import Protocol
from ..db_manager.db_operation import db
from .. dispatch.job_dispatch import NodeDisPatch
from twisted.internet.defer import Deferred
import xmlrpclib
import time

num = 0

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


class NodeProtocol(Protocol):

    def __init__(self):
        self.name = ""  # 当前实例的名字
        self.weight = 0
        self.cur_weight = 0
        self.id = ""
        self.rpc_address = ""
        self.status = False
        self.work_number = 0
        self.error_info = ["<a>生成失败</a>", "<a>超过最大重试次数</a>", "<a>no slave</a>", "<a>任务超时</a>"]
        self.normal_info = ['<a>正在生成</a>']
        self.finish_info = ["<a>点击下载</a>"]

    def connectionMade(self):
        pass

    def write(self, data):
        self.transport.write(data + "#####")

    def connectionLost(self, reason=''):
        if self.status:
            print 'Node Client {} lost, the reason is  {}'.format(self.name, reason)
            self.factory.OnlineProtocol.del_client(self.name)
            self.status = False
        else:
            pass

    def dataReceived(self, _data):

        try:
            data_list = _data.split("#####")
            data_list.remove("")
            for data in data_list:
                temp = json.loads(data)
                if not self.name:  # 如果是第一次连接 设置结点的权重和对应的名称 成功返回 200
                    status = self.factory.OnlineProtocol.id_name_map.get(temp.get('id'))
                    if status:
                        self.write(json.dumps({"status": 403}))
                        self.connectionLost()
                    global num
                    self.name = 'node' + str(num)
                    num += 1
                    self.weight = int(temp['weight'])
                    self.id = temp['id']
                    self.rpc_address = temp['rpc_address']
                    print 'node Client {} Connection '.format(self.name)
                    self.factory.OnlineProtocol.add_client(self.name, self)  # 把该结点放到在线结点中
                    self.status = True
                    self.factory.OnlineProtocol.id_name_map[temp['id']] = self.name  # id 与 名称的映射
                    self.write(json.dumps({"status": 200}))
                else:

                    """
                     获取当前id 对应的 div_name 若发送结点的id与div_name不搭说明已经id已经被占用 则拒绝连接 返回错误码 403
                     """
                    result = self.info_check(temp)
                    if result:
                        self.write(json.dumps(result))
                        return
                    if NodeDisPatch.work.get(temp.get('task_id')):
                        NodeDisPatch.work[temp.get('task_id')] = temp
                # db.execute_insert('sensor', temp.keys(), [temp[key] for key in temp.keys()])
                        for observe in self.factory.OnlineProtocol.observe.get('user' + str(temp.get('user_id'))):
                            # 观察者模式　发送给所有关注该结点的sockjs
                            observe.transport.write(json.dumps(temp))
                        self.write(json.dumps({"status": 200}))
                    else:
                        self.write(json.dumps({"status": 404, "task".format(temp.get("task_id")): "failed"}))
        except Exception as e:
            self.write(json.dumps({"status": 500, "info": str(e)}))
            self.connectionLost(e)

    def info_check(self, info):
        _time = info['entry_time']
        time_list = time.strptime(_time, '%Y-%m-%d %H:%M:%S')
        total = time.mktime(time_list)
        cur = int(time.time())
        node_list = self.factory.OnlineProtocol.get_online_protocols("node")
        if cur - total > 10:
            return {"status": 501, "info": "时间超时，无效信息!"}
        if info['status'] == "work" and info['result'] not in self.normal_info:
            return {"status": 501, "info": "当前状态是 work 但是状态为".format(info['result'])}
        if info['status'] == 'failed' and info['result'] not in self.error_info:
            return {"status": 501, "info": "当前状态是 failed 但是状态为".format(info['result'])}
        if info['status'] == "finish" and info['result'] not in self.finish_info:
            return {"status": 501, "info": "当前状态是 finish 但是状态为".format(info['result'])}
        if node_list and info['result'] == "<a>no slave</a>":
            return {"status": 501, "info": "当前存在结点 但是状态为".format(info['result'])}
        return {}

    def success(self, info):
        for observe in self.factory.OnlineProtocol.observe.get(self.name):
            # 观察者模式　发送给所有关注该结点的sockjs
            observe.transport.write(json.dumps(info))

    def failed(self, info):
        print "".format(self.name) + str(info)

    def get_node_info(self):
        if self.status:
            d = Deferred()
            d.addCallbacks(self.success, self.failed)
            try:
                rpc_server = xmlrpclib.Server("http://{}".format(self.rpc_address))
                rpc_info = rpc_server.get_node_info()
                rpc_info['name'] = self.name
                if self.factory.OnlineProtocol.cache.get(self.name) and \
                        len(self.factory.OnlineProtocol.cache.get(self.name)) == self.factory.OnlineProtocol.length:
                    self.factory.OnlineProtocol.cache.get(self.name).pop(0)
                self.factory.OnlineProtocol.cache.get(self.name).append(rpc_info)
                d.callback(rpc_info)
            except Exception as e:
                d.errback(e)

    def __str__(self):
        return json.dumps({'id': self.id, "weight": self.weight, "rpc_address": self.rpc_address, "name": self.name})
