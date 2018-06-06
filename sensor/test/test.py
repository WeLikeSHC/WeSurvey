# coding=utf-8
from twisted.web import xmlrpc, server


import xmlrpclib

s = xmlrpclib.Server("http://localhost:5003")

temp = s.get_online_protocol()
print len(temp['3'])
print temp['3'][0]
