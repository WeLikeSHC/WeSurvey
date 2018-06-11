# coding=utf-8

from twisted.web import xmlrpc
from onlineProtocol import online


class StateRpc(xmlrpc.XMLRPC):
    """
        提供给web应用的一些相关数据
    """

    # 当前在线的protocol实例的名称列表
    def xmlrpc_get_online_protocol(self):
        return [(key, items[0]) for (key, items) in online.cache.items() if key.startswith("sensor") and items]

    def xmlrpc_get_online_sock(self):
        return [key for key in online.cache.keys() if key.startswith("sockjs")]


Rpc = StateRpc()
