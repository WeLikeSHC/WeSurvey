# coding=utf-8

"""
用于更新node结点的状态
"""

import json
from twisted.internet.protocol import Protocol


class NodeUiProtocol(Protocol):

    num = 0

    def __init__(self):
        self.name = ""  # 当前实例的名字
        self.div_name = ""  # 观察者对象

    def connectionMade(self):
        self.name = 'taskjs' + str(NodeUiProtocol.num + 1)
        NodeUiProtocol.num += 1
        print 'taskjs Client {} Connection '.format(self.name)
        self.factory.OnlineProtocol.add_client(self.name, self)

    def connectionLost(self, reason=''):
        print 'taskjs Client {} lost, the reason is  {}'.\
            format(self.name, reason)
        self.factory.OnlineProtocol.del_client(self.name)
        if self.factory.OnlineProtocol.observe.get(self.div_name):
            if self in self.factory.OnlineProtocol.observe.get(self.div_name):
                self.factory.OnlineProtocol.observe.get(self.div_name).remove(self)
                print '{} Client has lost a observe {}'.format(self.div_name, self.name)

    def dataReceived(self, data):

        try:
            self.div_name = 'user' + json.loads(data)["user_id"]
            if self.factory.OnlineProtocol.observe. has_key(self.div_name):
                if self not in self.factory.OnlineProtocol.observe.get(self.div_name):
                    self.factory.OnlineProtocol.observe.get(self.div_name).append(self)
                    print '{} Client has append a observe {}'.format(self.div_name, self.name)
            else:
                self.transport.write(json.dumps({'error': 'not existed!'}))
                self.transport.loseConnection()
        except Exception as e:
            self.transport.loseConnection()
            print e, "node_ui_lost"
