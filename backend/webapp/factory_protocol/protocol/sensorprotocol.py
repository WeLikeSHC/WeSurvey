# coding=utf-8

import json
from twisted.internet.protocol import Protocol
from ..db_manager.db_operation import db
import queue

q = queue.Queue()
q.put(0)


class SensorProtocol(Protocol):

    def __init__(self):
        self.name = ""  # 当前实例的名字
        self.status = False
        self.id = ""

    def connectionMade(self):
        pass

    def connectionLost(self, reason=''):
        if self.status:
            print 'Sensor Client {} lost, the reason is  {}'.format(self.name, reason)
            q.put(q.get() - 1)
            self.factory.OnlineProtocol.del_client(self.name)
            for (key, items) in self.factory.OnlineProtocol.id_name_map.items():
                if items == self.name:
                    del self.factory.OnlineProtocol.id_name_map[key]
            self.status = False
        else:
            pass

    def dataReceived(self, data):

        try:
            if self.factory.OnlineProtocol.cache.get(self.name) and \
                    len(self.factory.OnlineProtocol.cache.get(self.name)) == self.factory.OnlineProtocol.length:
                self.factory.OnlineProtocol.cache.get(self.name).pop(0)

            temp = json.loads(data)

            status = self.factory.OnlineProtocol.id_name_map.get(temp.get('id'))

            """
            获取当前id 对应的 div_name 若发送结点的id与div_name不搭说明已经id已经被占用 则拒绝连接 返回错误码 403
            """

            if status and status != self.name:
                    self.transport.write(json.dumps({"status": 403}))
                    self.connectionLost()
            else:
                if not self.name:
                    num = q.get() + 1
                    self.name = 'sensor' + str(num)
                    q.put(num)
                    self.status = True
                    self.id = temp.get('id')
                    print 'Sensor Client {} Connection '.format(self.name)
                    self.factory.OnlineProtocol.add_client(self.name, self)
                    self.factory.OnlineProtocol.id_name_map[temp['id']] = self.name
                self.factory.OnlineProtocol.cache.get(self.name).append(temp)
                # db.execute_insert('sensor', temp.keys(), [temp[key] for key in temp.keys()])
                for observe in self.factory.OnlineProtocol.observe.get(self.name):  # 观察者模式　发送给所有关注该结点的sockjs
                    observe.transport.write(json.dumps(temp))
                self.transport.write(json.dumps({"status": 200}))

        except Exception as e:
            self.transport.write(json.dumps({"status": 500}))
            self.connectionLost()
            print e
