# coding=utf-8

from twisted.internet import reactor
from onlineProtocol import online
from factory_protocol.protocol.sensorprotocol import SensorProtocol
from factory_protocol.factory.sensorfactory import SensorFactory
from factory_protocol.protocol.SendUi import SendUiProtocol
from factory_protocol.factory.SendUiFactory import SendUiFactory
from stateRPC import Rpc
from twisted.web import resource, server
from txsockjs.factory import SockJSResource
from twisted.internet import endpoints
from config import config

sensor = SensorFactory('SensorFactory', SensorProtocol)
sensor.OnlineProtocol = online
reactor.listenTCP(int(config.listen_port), sensor)  # 把工厂和端口进行绑定

rpc_point = endpoints.TCP4ServerEndpoint(reactor, int(config.rpc_port))
rpc_point.listen(server.Site(Rpc))  # 把资源和对应的端口进行绑定

send_data = SendUiFactory("SendUiFactory", SendUiProtocol)
send_data.OnlineProtocol = online
root = resource.Resource()

root.putChild('show_data', SockJSResource(send_data))

site = server.Site(root)
reactor.listenTCP(int(config.ui_port), site)

reactor.run()
