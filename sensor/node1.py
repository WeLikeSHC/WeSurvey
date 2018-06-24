# coding=utf-8

from init_pro import ConnectionFactory, ConnectionProtocol, Connector
import sys
from twisted.internet import reactor
from twisted.python import log
import random
from twisted.web import xmlrpc
import json
from twisted.web import server
from twisted.internet import endpoints
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
        self.status = False
        self.instance = None

    def create_long_connection(self):

        """建立长连接"""
        if not len(Connector.get_online_protocol('ConnectionPlatform')):
            print u"未连接........................"
            reactor.connectTCP(self.host, self.port, self.long_connection)
            print u"正在重连........................"
            self.status = False
            self.instance = None
        else:
            if self.status is False:
                self.instance = Connector.get_online_protocol('ConnectionPlatform')[0]
                self.status = True
                self.instance.transport.write(json.dumps(self.pack_data()))
                self.instance.work = None
                print u"已发送采集的到的数据....................."
            else:
                if self.instance.work:
                    self.instance.work['schedule'] = 0.5
                    self.instance.work['entry_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    self.instance.work['status'] = 'work'
                    print self.instance.work['task_id'], "success"
                    self.instance.transport.write(json.dumps(self.instance.work))
        reactor.callLater(1, self.create_long_connection)  # 一直尝试在连接

    @staticmethod
    def pack_data():

        info = dict()
        info["id"] = '1'
        info['weight'] = 50
        info['rpc_address'] = "127.0.0.1:5005"
        return info

    # @staticmethod
    # def pack_job_info():
    #     data = dict()
    #     data['task_id'] = self.task_id
    #     data['node_id'] = node.id
    #     data['status'] = 'work'
    #     data['schedule'] = 0.0
    #     data['entry_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    #     self.work[data['task_id']] = data
    #     online.observe['task' + data['task_id']] = list()


create_connection = CreateConnection('127.0.0.1', 5004)
create_connection.create_long_connection()


class StateRpc(xmlrpc.XMLRPC):
    """
        提供给web应用的一些相关数据
    """

    def xmlrpc_add_job(self, data):  # 提供的接收任务的接口
        if create_connection.instance:
            create_connection.instance.work = data
            create_connection.instance.work_num += 1
            create_connection.instance.cur_weight = data['cur_weight']
            return {'status': 200}
        else:
            return {"status": 500, "info": "no master"}

    def xmlrpc_get_node_info(self):
        return {"memory_use": random.uniform(0, 1), "memory_total": "15GB", "cpu_use": random.uniform(0, 1), "cpu_total": "8个",
                "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "network_receive": "1.2M/s", "network_launch": "1.2M/s", "disk_use": random.uniform(0, 1),
                "disk_total": "1000TB",
                "work_number": create_connection.instance.work_num, "cur_weight": create_connection.instance.cur_weight,
                "weight": create_connection.instance.weight}


rpc = StateRpc()
rpc_point = endpoints.TCP4ServerEndpoint(reactor, 5005)
rpc_point.listen(server.Site(rpc))  # 把资源和对应的端口进行绑定

reactor.run()
