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
        self.instance = None

    def create_long_connection(self):

        """建立长连接"""
        if not len(Connector.get_online_protocol('ConnectionPlatform')):
            print u"未连接........................"
            reactor.connectTCP(self.host, self.port, self.long_connection)
            print u"正在重连........................"
            self.instance = None
        else:
            self.instance = Connector.get_online_protocol('ConnectionPlatform')[0]
            self.instance.transport.write(json.dumps(self.pack_data()))
            print u"已发送心跳包....................."

        reactor.callLater(1, self.create_long_connection)  # 一直尝试在连接

    @staticmethod
    def pack_data():

        info = dict()
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
            create_connection.instance.work.append(data)
            print len(create_connection.instance.work)
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

    def xmlrpc_kill_task(self, task_id):
        for work in create_connection.instance.work:
            if work['task_id'] == task_id:
                work['entry_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                work['status'] = 'failed'
                work['result'] = '<a>生成失败</a>'
                create_connection.instance.work_num -= 1
                create_connection.instance.transport.write(json.dumps([work]))
                create_connection.instance.work.remove(work)
                return {"status": 200}
        return {"status": 404}


rpc = StateRpc()
rpc_point = endpoints.TCP4ServerEndpoint(reactor, 5005)
rpc_point.listen(server.Site(rpc))  # 把资源和对应的端口进行绑定

reactor.run()
