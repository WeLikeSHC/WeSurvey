# coding=utf-8


import xmlrpclib

s = xmlrpclib.Server("http://localhost:5007")

data = {"user_id": 1, 'url': "www.baidu.com", "num": 10, "dispersion": 5, "type": True, "func": ""}

print s.kill_task("1")