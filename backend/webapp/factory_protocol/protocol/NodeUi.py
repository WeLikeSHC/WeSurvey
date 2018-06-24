# coding=utf-8

"""
用于更新node结点的状态
"""

import json
from twisted.internet.protocol import Protocol

num = 0


class NodeUiProtocol(Protocol):

    def __init__(self):
        self.name = ""  # 当前实例的名字
        self.div_name = ""  # 观察者对象

    def connectionMade(self):
        global num
        self.name = 'taskjs' + str(num + 1)
        num += 1
        print 'taskjs Client {} Connection '.format(self.name)
        self.factory.OnlineProtocol.add_client(self.name, self)

    def connectionLost(self, reason=''):
        print 'taskjs Client {} lost, the reason is  {}'.\
            format(self.name, reason)
        self.factory.OnlineProtocol.del_client(self.name)
        if self.factory.OnlineProtocol.observe.get(self.div_name):
            print '{} Client has lost a observe {}'.format(self.div_name, self.name)
            self.factory.OnlineProtocol.observe.get(self.div_name).remove(self)

    def dataReceived(self, data):

        try:
            self.div_name = 'user' + json.loads(data)["user_id"]
            if self.factory.OnlineProtocol.observe. has_key(self.div_name):
                if self not in self.factory.OnlineProtocol.observe.get(self.div_name):
                    self.factory.OnlineProtocol.observe.get(self.div_name).append(self)
                    print '{} Client has append a observe {}'.format(self.div_name, self.name)
            else:
                self.transport.write(json.dumps({'error': 'not existed!'}))
        except Exception as e:
            print e
