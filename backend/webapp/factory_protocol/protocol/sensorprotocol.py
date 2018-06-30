# coding=utf-8

import json
from twisted.internet.protocol import Protocol
# from ..db_manager.db_operation import db


class SensorProtocol(Protocol):

    num = 0

    def __init__(self):
        self.name = ""  # 当前实例的名字

    def connectionMade(self):
        self.name = 'sensor' + str(SensorProtocol.num)
        SensorProtocol.num += 1
        print 'Sensor Client {} Connection '.format(self.name)
        self.factory.OnlineProtocol.add_client(self.name, self)
        self.factory.OnlineProtocol.observe[self.name] = list()
        self.factory.OnlineProtocol.cache[self.name] = list()

    def connectionLost(self, reason=''):
        print 'Sensor Client {} lost, the reason is  {}'.format(self.name, reason)
        self.factory.OnlineProtocol.del_client(self.name)
        del self.factory.OnlineProtocol.observe[self.name]
        del self.factory.OnlineProtocol.cache[self.name]

    def dataReceived(self, data):

        try:

            temp = json.loads(data)
            if self.factory.OnlineProtocol.cache.get(self.name) and \
                    len(self.factory.OnlineProtocol.cache.get(self.name)) == self.factory.OnlineProtocol.length:
                self.factory.OnlineProtocol.cache.get(self.name).pop(0)

            temp['id'] = self.name
            self.factory.OnlineProtocol.cache.get(self.name).append(temp)
            # db.execute_insert('sensor', temp.keys(), [temp[key] for key in temp.keys()])
            for observe in self.factory.OnlineProtocol.observe.get(self.name):  # 观察者模式　发送给所有关注该结点的sockjs
                observe.transport.write(json.dumps(temp))
            self.transport.write(json.dumps({"status": 200}))

        except Exception as e:
            self.transport.write(json.dumps({"status": 500}))
            self.transport.loseConnection()
            print e
