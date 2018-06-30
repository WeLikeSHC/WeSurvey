# coding=utf-8

import json
from twisted.internet.protocol import Protocol
# from ..db_manager.db_operation import db
from twisted.internet import reactor
import xmlrpclib
import datetime
from twisted.internet.threads import deferToThread
import time


class NodeProtocol(Protocol):

    num = 0

    def __init__(self):
        self.name = ""  # 当前实例的名字
        self.weight = 0
        self.cur_weight = 0
        self.rpc_address = ""
        self.work_number = 0
        self.last_check = ""

    def connectionMade(self):
        self.name = 'node' + str(NodeProtocol.num)
        NodeProtocol.num += 1
        print 'node Client {} Connection '.format(self.name)
        self.last_check = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.factory.OnlineProtocol.observe[self.name] = list()
        self.factory.OnlineProtocol.cache[self.name] = list()
        self.factory.OnlineProtocol.add_client(self.name, self)  # 把该结点放到在线结点中
        reactor.callLater(5, self.check_alive)

    def connectionLost(self, reason=''):
        print 'Node Client {} lost, the reason is  {}'.format(self.name, reason)
        self.factory.OnlineProtocol.del_client(self.name)
        del self.factory.OnlineProtocol.observe[self.name]
        del self.factory.OnlineProtocol.cache[self.name]

    def dataReceived(self, data):  # 心跳包
        try:
            temp = json.loads(data)
            self.weight = int(temp['weight'])
            self.rpc_address = temp['rpc_address']
            self.last_check = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            # print u'node Client {} 发送了心跳包,　当前时间为{} '.format(self.name, self.last_check)
            self.transport.write(json.dumps({"status": 200}))
        except Exception as e:
            self.transport.write(json.dumps({"status": 500, "info": str(e)}))
            self.transport.loseConnection()

    def success(self, info):

        info['name'] = self.name
        if self.factory.OnlineProtocol.cache.get(self.name) and \
                len(self.factory.OnlineProtocol.cache.get(self.name)) == self.factory.OnlineProtocol.length:
            self.factory.OnlineProtocol.cache.get(self.name).pop(0)

        self.factory.OnlineProtocol.cache.get(self.name).append(info)
        for observe in self.factory.OnlineProtocol.observe.get(self.name):
            # 观察者模式　发送给所有关注该结点的sockjs
            observe.transport.write(json.dumps(info))
        return "发送结点 {}　信息成功".format(self.name)

    def failed(self, info):
        print "".format(self.name) + str(info)

    def get_node_info(self):
        rpc_server = xmlrpclib.Server("http://{}".format(self.rpc_address))
        rpc_info = deferToThread(rpc_server.get_node_info)
        rpc_info.addCallbacks(self.success, self.failed)
        rpc_info.addCallbacks(self.failed, self.failed)

    def check_alive(self):
        time_list = time.strptime(self.last_check, '%Y-%m-%d %H:%M:%S')
        total = time.mktime(time_list)
        cur = int(time.time())
        if cur - total > 5:
            self.transport.loseConnection()
        reactor.callLater(5, self.check_alive)

    def __str__(self):
        return json.dumps({"last_check": self.last_check,
                           "weight": self.weight, "rpc_address": self.rpc_address, "name": self.name})

