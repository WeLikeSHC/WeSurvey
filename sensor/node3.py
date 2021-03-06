# coding=utf-8

from init_pro import ConnectionFactory, ConnectionProtocol, Connector
import sys
from twisted.python import log
from twisted.web import xmlrpc
import requests
import json
from twisted.internet import reactor
from twisted.web import server
from twisted.internet import endpoints
import datetime
from node_info import Monitor

log.startLogging(sys.stdout)


def sigInt(*args, **kwargs):
    print args, kwargs
    Monitor.status = False
    reactor.stop()


reactor.sigInt = sigInt


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
            reactor.callLater(1, self.pack_job_info)
            self.instance = Connector.get_online_protocol('ConnectionPlatform')[0]
            self.instance.transport.write(json.dumps(self.pack_data()))
            print u"已发送心跳包....................."

        reactor.callLater(1, self.create_long_connection)  # 一直尝试在连接

    @staticmethod
    def pack_data():

        info = dict()
        info['weight'] = 50
        info['rpc_address'] = "192.168.1.185:5007"
        return info

    @staticmethod
    def send_http(data):
        headers = {'Content-Type': 'application/json'}
        body = json.dumps(data)
        url = "http://127.0.0.1:5003/post_data"
        r = requests.session().post(url, data=body, headers=headers)
        print r.text

    def pack_job_info(self):
        for data in self.instance.work:
            data['status'] = 'work'
            data['schedule'] = 0.0
            data['result'] = '<a>Being generated</a>'
            data['entry_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            print "send http information ..."
            CreateConnection.send_http(data)

        # reactor.callLater(1, CreateConnection.pack_job_info)


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
        return {"memory_use": Monitor['memory_use'], "memory_total": Monitor['memory_total'],
                "cpu_use": Monitor['cpu_use'], "cpu_total": Monitor['cpu_total'],
                "time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "network_receive": Monitor['network_receive'], "network_launch": Monitor['network_launch'],
                "disk_use": Monitor['disk_use'], "disk_total": Monitor['disk_total'],
                "work_number": len(create_connection.instance.work), "cur_weight": create_connection.instance.cur_weight,
                "weight": create_connection.instance.weight}

    def xmlrpc_kill_task(self, task_id):
        for work in create_connection.instance.work:
            if work['task_id'] == task_id:
                work['entry_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                work['status'] = 'failed'
                work['result'] = '<a>Generation failure</a>'
                create_connection.instance.work_num -= 1
                create_connection.send_http(work)
                create_connection.instance.work.remove(work)
                return {"status": 200}
        return {"status": 404}


def print_info(*args, **kwargs):
    if args or kwargs:
        print args, kwargs


rpc = StateRpc()
rpc_point = endpoints.TCP4ServerEndpoint(reactor, 5007)
rpc_point.listen(server.Site(rpc))  # 把资源和对应的端口进行绑定
reactor.run()
