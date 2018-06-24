# coding=utf-8

"""
用于更新node结点的状态
"""

import json
from twisted.internet.protocol import Protocol

num = 0


class NodeInfoUiProtocol(Protocol):

    def __init__(self):
        self.name = ""  # 当前实例的名字
        self.div_name = ""  # 观察者对象

    def connectionMade(self):
        global num
        self.name = 'infojs' + str(num + 1)
        num += 1
        print 'infojs Client {} Connection '.format(self.name)
        self.factory.OnlineProtocol.add_client(self.name, self)

    def connectionLost(self, reason=''):
        print 'infojs Client {} lost, the reason is  {}'.\
            format(self.name, reason)
        self.factory.OnlineProtocol.del_client(self.name)
        if self.factory.OnlineProtocol.observe.get(self.div_name):
            print '{} Client has lost a observe {}'.format(self.div_name, self.name)
            self.factory.OnlineProtocol.observe.get(self.div_name).remove(self)

    def dataReceived(self, data):
        """
        当前第一次连接时返回所有的缓存数据
        之后通过观察者模式 单个分发
        :param data:
        :return:
        """
        try:
            self.div_name = json.loads(data)["node_name"]
            if self.factory.OnlineProtocol.online_protocol.get(self.div_name):
                if self not in self.factory.OnlineProtocol.observe.get(self.div_name):
                    self.factory.OnlineProtocol.observe.get(self.div_name).append(self)
                    print '{} Client has append a observe {}'.format(self.div_name, self.name)
                    self.transport.write(json.dumps(self.factory.OnlineProtocol.cache.get(self.div_name)))
            else:
                self.transport.write(json.dumps({"status": 404}))
        except Exception as e:
            print e
