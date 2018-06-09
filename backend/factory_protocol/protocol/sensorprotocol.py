# coding=utf-8

import json
from twisted.internet.protocol import Protocol
from backend.db_manager.db_operation import db

num = 0


class SensorProtocol(Protocol):

    def __init__(self):
        self.name = ""  # 当前实例的名字

    def connectionMade(self):
        global num
        self.name = 'sensor' + str(num + 1)
        num += 1
        print 'Sensor Client {} Connection '.format(self.name)
        self.factory.OnlineProtocol.add_client(self.name, self)

    def connectionLost(self, reason=''):
        print 'Sensor Client {} lost, the reason is  {}'.\
            format(self.name, reason)
        self.factory.OnlineProtocol.del_client(self.name)

    def dataReceived(self, data):

        try:
            if len(self.factory.OnlineProtocol.cache.get(self.name)) == self.factory.OnlineProtocol.length:
                self.factory.OnlineProtocol.cache.get(self.name).pop(0)
            temp = json.loads(data)
            self.factory.OnlineProtocol.cache.get(self.name).append(temp)
            db.execute_insert('sensor', temp.keys(), [temp[key] for key in temp.keys()])
            for observe in self.factory.OnlineProtocol.observe.get(self.name):  # 观察者模式　发送给所有关注该结点的sockjs
                observe.transport.write(json.dumps(temp))
        except Exception as e:
            print 'sensor'
            print e
