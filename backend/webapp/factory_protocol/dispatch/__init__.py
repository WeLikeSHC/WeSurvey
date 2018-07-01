# coding=utf-8

"""
node 结点协议

当创建连接时, 传递结点的参数 包括 id 和 权值 id 为结点名称, 结点所在rpc服务器地址

{'id':'slave1', 'weight': 20, 'rpc_address':"127.0.0.1:5003"}

当非第一次连接时，发送的是实时的消息 更新任务的实时状态
格式如:

更新某个任务的状态

json 格式中 status 为信息状态 表示这条信息是否正常 正常为 200 异常为 500

id 为slave结点的id号

task_id 为 任务的编号

entry_time 为更新时间

task_status 为任务状态

schedule 为任务进度

{'status':200, 'id': 1 ,'task_id':'1', 'entry_time':'2017-2-2', 'task_status':'working', 'schedule':0.02}

某个任务成功
{'status':200, 'id': 1, 'task_id':'1', 'entry_time':'2017-2-2', 'task_status':'finish', 'schedule':1}

某个任务失败

{'status':200, 'id': 1, 'task_id':'1', 'entry_time':'2017-2-2', 'task_status':'failed', 'schedule':1}

发送异常信息

{'status':500, 'id': 1, 'info':"error info"}

"""