# coding=utf-8

from twisted.web import xmlrpc, server
from twisted.internet import reactor, endpoints
from backend.webapp.onlineProtocol import online


class StateRpc(xmlrpc.XMLRPC):
    """
        提供给web应用的一些相关数据
    """

    def xmlrpc_add_job(self, user_id, data):  # 提供的接收任务的接口
        print data


Rpc = StateRpc()
rpc_point = endpoints.TCP4ServerEndpoint(reactor, 6000)
rpc_point.listen(server.Site(Rpc))
reactor.run()