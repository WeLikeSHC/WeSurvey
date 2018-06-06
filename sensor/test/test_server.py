# coding=utf-8
from twisted.internet import reactor

from twisted.web import xmlrpc, server


class Example(xmlrpc.XMLRPC):

    def xmlrpc_echo(self, x):
        return x

    def xmlrpc_add(self, a, b):
        return a + b

    def xmlrpm_fault(self):
        raise xmlrpc.Fault(123, "The fault procedure is faulty.")


R = Example()
reactor.listenTCP(5000, server.Site(R))
print "http://localhost:5000"
reactor.run()
