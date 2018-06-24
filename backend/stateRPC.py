# coding=utf-8

from twisted.web import xmlrpc
from backend.webapp.onlineProtocol import online
import json
from webapp.factory_protocol.dispatch.job_dispatch import NodeDisPatch


class StateRpc(xmlrpc.XMLRPC):
    """
        提供给web应用的一些相关数据
    """

    # 当前在线的protocol实例的名称列表
    def xmlrpc_get_online_protocol(self):
        return [(key, items[0]) for (key, items) in online.cache.items() if key.startswith("sensor") and items]

    def xmlrpc_get_online_sock(self):
        return [key for key in online.cache.keys() if key.startswith("sockjs")]

    def xmlrpc_add_job(self, data):  # 提供的接收任务的接口
        return NodeDisPatch.put_data(json.loads(data))

    def xmlrpc_get_online_node(self):
        temp = online.get_online_protocol
        return [str(temp(key)) for key in online.cache.keys() if key.startswith("node")]


Rpc = StateRpc()
