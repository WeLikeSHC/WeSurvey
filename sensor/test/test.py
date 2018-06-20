# coding=utf-8


import xmlrpclib

s = xmlrpclib.Server("http://localhost:5001")

temp = s.get_online_protocol()
print s.get_online_sock()

data = {"user_id": 1, 'url': "www.baidu.com", "num": 10, "dispersion": 5, "type": True, "func": ""}

print s.add_job(data)
