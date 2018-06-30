# coding=utf-8

from init_pro import ConnectionFactory, ConnectionProtocol, Connector
import sys
from twisted.internet import reactor
from twisted.python import log
import random
import json
import datetime

log.startLogging(sys.stdout)


class CreateConnection(object):
    """
        创建主动的长连接
    """
    def __init__(self, host, port):
        self.long_connection = ConnectionFactory('ConnectionPlatform', ConnectionProtocol)
        self.long_connection.onlineProtocol = Connector
        self.host = host
        self.port = port

    def create_long_connection(self):

        """建立长连接"""
        if not len(Connector.get_online_protocol('ConnectionPlatform')):
            print u"未连接........................"
            reactor.connectTCP(self.host, self.port, self.long_connection)
            print u"正在重连........................"

        else:
            Connector.get_online_protocol('ConnectionPlatform')[0].\
                transport.write(json.dumps(self.pack_data()))
            print u"已发送采集的到的数据....................."

        reactor.callLater(1, self.create_long_connection)           # 一直尝试在连接

    @staticmethod
    def pack_data():

        info = dict()
        info["entry_time"] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        info["entry_data"] = random.uniform(-10, 50)
        info["info"] = "null"
        info['type'] = 'mois'
        info['name'] = 'cherrymonth'
        info['user_id'] = '1'
        return info


create_connection = CreateConnection('127.0.0.1', 5002)
create_connection.create_long_connection()
reactor.run()
