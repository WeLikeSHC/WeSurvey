# coding=utf-8

from twisted.internet import reactor
from onlineProtocol import online
from factory_protocol.protocol.sensorprotocol import SensorProtocol
from factory_protocol.factory.sensorfactory import SensorFactory
from stateRPC import Rpc
from twisted.internet import endpoints
from twisted.web import server

sensor = SensorFactory('SensorFactory', SensorProtocol)
sensor.OnlineProtocol = online
reactor.listenTCP(5002, sensor)
rpc_point = endpoints.TCP4ServerEndpoint(reactor, 5003)
rpc_point.listen(server.Site(Rpc))
reactor.run()
