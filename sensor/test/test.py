# coding=utf-8


import xmlrpclib

s = xmlrpclib.Server("http://localhost:5001")

temp = s.get_online_sock()
print temp
