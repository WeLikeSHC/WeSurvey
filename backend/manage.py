# coding=utf-8

from twisted.internet import reactor
from backend.webapp.onlineProtocol import online
from webapp.factory_protocol.protocol.sensorprotocol import SensorProtocol
from webapp.factory_protocol.factory.sensorfactory import SensorFactory
from webapp.factory_protocol.protocol.SendUi import SendUiProtocol
from webapp.factory_protocol.factory.SendUiFactory import SendUiFactory
from webapp.factory_protocol.protocol.NodeInfoUi import NodeInfoUiProtocol
from webapp.factory_protocol.factory.NodeFactory import NodeFactory
from webapp.factory_protocol.protocol.NodeUi import NodeUiProtocol
from webapp.factory_protocol.protocol.node_protocol import NodeProtocol
from webapp.factory_protocol.resource.node_info import NodePage
from stateRPC import Rpc
from webapp.factory_protocol.dispatch.node_info_dispatch import TaskDispatch
from twisted.web import resource, server
from txsockjs.factory import SockJSResource
from twisted.internet import endpoints
from webapp.config import config

sensor = SensorFactory('SensorFactory', SensorProtocol)
sensor.OnlineProtocol = online
reactor.listenTCP(int(config.listen_port), sensor)  # 把工厂和端口进行绑定

node = NodeFactory("NodeFactory", NodeProtocol)
node.OnlineProtocol = online
reactor.listenTCP(int(config.slave_port), node)

rpc_point = endpoints.TCP4ServerEndpoint(reactor, int(config.rpc_port))
rpc_point.listen(server.Site(Rpc))  # 把资源和对应的端口进行绑定

send_data = SendUiFactory("SendUiFactory", SendUiProtocol)
send_data.OnlineProtocol = online

send_js = SensorFactory('SensorJSFactory', NodeInfoUiProtocol)  # 展示结点状态
send_js.OnlineProtocol = online

send_work = SensorFactory('SensorJSFactory', NodeUiProtocol)
send_work.OnlineProtocol = online

root = resource.Resource()
TaskDispatch.OnlineProtocol = online
root.putChild('show_data', SockJSResource(send_data))
root.putChild("post_data", NodePage())
root.putChild('show_job', SockJSResource(send_work))
root.putChild('show_js', SockJSResource(send_js))  # 接收js 数据并把结点的状态显示在网页上

site = server.Site(root)
reactor.listenTCP(int(config.ui_port), site)

reactor.run()
