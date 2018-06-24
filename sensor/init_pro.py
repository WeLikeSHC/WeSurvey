# coding=utf-8

from twisted.internet.protocol import ClientFactory, Protocol
import re
import json


class ConnectionFactory(ClientFactory):
    """
        主动连接数据采集服务器平台的实例工厂
        属于Client 建立长连接
        主动建立连接
    """
    def __init__(self, name=None, protocol=None):
        self.instanceFactoryName = name  # 实例名
        self.protocol = protocol  # 实例
        self.numProtocols = 0  # 实例数目
        self.onlineProtocol = None

        print self.instanceFactoryName + 'Client start connecting '
        return


class ConnectionProtocol(Protocol):
    """
        用于创建主动连接数据采集平台的实例
    """

    def __init__(self):
        self.div_name = ""
        self.status = False
        self.weight = 50
        self.cur_weight = 50
        self.work_num = 0

    def connectionMade(self):
        # 工厂创建的protocol数目增加一个
        self.factory.numProtocols += 1
        # 给API到UI的传输实例命名
        self.div_name = 'ConnectionPlatform'
        print "Connection successful, the current number of ConnectionPlatform is " + str(self.factory.numProtocols)
        self.factory.onlineProtocol.add_client(self.div_name, self)  # 添加到在线列表里
        self.status = True

    def connectionLost(self, reason=""):
        # 连接丢失，删除实例
        if self.status:
            print "The reason of ConnectionPlatform lost is " + str(reason) + "\n"
            self.factory.numProtocols -= 1
            print "the current number of ConnectionPlatform is " + str(self.factory.numProtocols) + "\n"
            self.factory.onlineProtocol.del_client(self.div_name)
            self.status = False
        else:
            pass

    def dataReceived(self, data):
        try:
            print data
            json_data = json.loads(data)
            if json_data['status'] == 200:
                print "success"
            elif json_data['status'] == 404:
                print 'not find'
            elif json_data['status'] == 403:
                self.connectionLost('node existed !')
            else:
                self.connectionLost("some thing error")
        except Exception as e:
            print e


class Connector(object):
    """Connector维护了一个列表，用来登记各通信实体的在线状态"""

    def __init__(self):
        # 存放在线设备字典， 其中存储的是各个protocol的实例名,实现protocol的通信
        self.online_protocol = {}

    def get_online_protocol(self, div_name):

        # 返回一个实例列表 匹配参数div_name
        protocol_list = []
        pattern = re.compile(div_name)
        for i in self.online_protocol.keys():
            if pattern.match(i):
                protocol_list.append(self.online_protocol.get(i))
        return protocol_list

    def add_client(self, div_name, host):
        # 添加新设备到在线设备列表里
        self.online_protocol[div_name] = host
        print "Add " + div_name + " after, the current equipment is " + str(self.online_protocol)
        print '\n'

    def del_client(self, div_name):
        # 从在线设备列表里面删除这个设备
        if self.online_protocol.get(div_name):
            print "You want to delete " + div_name
            del self.online_protocol[div_name]
        else:
            print "Not Found the div you want to delete!"

        print "Delete " + div_name + " after, the current equipment is " + str(self.online_protocol)


Connector = Connector()
