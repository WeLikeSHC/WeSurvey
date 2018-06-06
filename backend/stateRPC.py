# coding=utf-8

from twisted.web import xmlrpc
from onlineProtocol import online


class StateRpc(xmlrpc.XMLRPC):
    """
        提供给web应用的一些相关数据
    """

    # 当前在线的protocol实例的名称列表
    def xmlrpc_get_online_protocol(self):

        temp = list()
        for key in online.cache.keys():
            temp.append(online.cache.get(key)[0].get('name'))
        return online.cache


Rpc = StateRpc()
