# coding=utf-8

import json
from twisted.internet.protocol import Protocol

num = 0


class SendUiProtocol(Protocol):

    def __init__(self):
        self.name = ""  # 当前实例的名字
        self.div_name = ""

    def connectionMade(self):
        global num
        self.name = 'sockjs' + str(num + 1)
        num += 1
        print 'SockJS Client {} Connection '.format(self.name)
        self.factory.OnlineProtocol.add_client(self.name, self)

    def connectionLost(self, reason=''):
        print 'SockJS Client {} lost, the reason is  {}'.\
            format(self.name, reason)
        self.factory.OnlineProtocol.del_client(self.name)
        if self.factory.OnlineProtocol.observe.get(self.div_name):
            print '{} Client has lost a observe {}'.format(self.div_name, self.name)
            self.factory.OnlineProtocol.observe.get(self.div_name).remove(self)

    def dataReceived(self, data):

        try:
            self.div_name = json.loads(data)["sensor_name"]
            if self.factory.OnlineProtocol.cache.get(self.div_name):
                if self not in self.factory.OnlineProtocol.observe.get(self.div_name):
                    self.factory.OnlineProtocol.observe.get(self.div_name).append(self)
                    print '{} Client has append a observe {}'.format(self.div_name, self.name)
                    self.transport.write(json.dumps(self.factory.OnlineProtocol.cache.get(self.div_name)))
            else:
                self.transport.write('error:not existed!')
        except Exception as e:
            print e
