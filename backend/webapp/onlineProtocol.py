# coding=utf-8

import re
from twisted.internet import reactor

"""
    此处主要为上线的小网关设备服务：
    程序初始化时：
        1.检测当前的设置文件中，所能控制的真实小网关
        2.软网关上线时，会保持住一个连接。
"""


class OnlineProtocol(object):

    def __init__(self):
        self.online_protocol = dict()
        self.cache = dict()  # 每个传感器的缓存数据
        self.length = 20
        self.observe = dict()  # 每个事件注册的观察者列表

    def get_online_protocol(self, div_name):

        # 返回一个实例, 从传递来的设备名 得到连接实例
        if self.online_protocol.get(div_name) is None:
            print ("Not Found This device,", div_name)
            return None
        else:
            return self.online_protocol.get(div_name)

    def get_online_protocols(self, div_name):

        # 得到部分匹配的所有在线实例
        protocols = []
        pattern = re.compile(div_name)
        for i in self.online_protocol.keys():
            if re.match(pattern, i):
                protocols.append(self.online_protocol.get(i))
        return protocols

    def add_client(self, div_name, host):

        # 添加新设备实例->到在线设备列表里 参数为实例和host
        self.online_protocol[div_name] = host
        print "Add " + div_name + " after, the current equipment is " + str(self.online_protocol.keys())

    def del_client(self, div_name):

        # 从在线设备列表里面删除这个设备
        if self.online_protocol.get(div_name):
            print "You want to delete " + div_name
            del self.online_protocol[div_name]
            print "Delete " + div_name + " after, the current equipment is " + str(self.online_protocol.keys())
        else:
            print "Not Found the div you want to delete!"

    def get_node_info(self):
        handler_list = [self.online_protocol.get(key) for key in self.online_protocol.keys() if key.startswith("node")]
        for handler in handler_list:
            # 上述方式存在问题　会导致图像不连续
            if self.observe.get(handler.name):  # 若该结点添加的存在观察者　则进行信息的查询
                handler.get_node_info()
        reactor.callLater(1, self.get_node_info)


online = OnlineProtocol()
reactor.callLater(1, online.get_node_info)
