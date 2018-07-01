# coding=utf-8

"""
实现任务的分发
"""


from twisted.internet.threads import deferToThread
from backend.webapp.onlineProtocol import online
import xmlrpclib
import json
from twisted.internet import reactor
import datetime
import time


class NodeDisPatch:

    def __init__(self):
        self.task_id = 0
        self.work = dict()
        self.OnlineProtocol = online

    def get_next_index(self):

        """
        平滑负载均衡算法
        先找到权重最大的结点分配给其任务 然后降低其权重
        并返回满足要求的结点
        :return:
        """

        total = 0
        index = -1
        node_list = self.OnlineProtocol.get_online_protocols("node")

        if not node_list:
            raise Exception("no slave can work.")

        for i in range(len(node_list)):
            node_list[i].cur_weight += node_list[i].weight
            total += node_list[i].weight
            if index == -1 or node_list[index].cur_weight < node_list[i].cur_weight:
                index = i

        node_list[index].cur_weight -= total
        return node_list[index]

    def add_job(self, data, user_id, overflow=False):

        """
        添加任务，若任务已经存在则可以覆盖掉之前的任务，重新运行
        :param data:
        :param user_id:
        :param overflow:
        :return:
        """

        result = {"status": 200}
        try:
            node = self.next_node
            if not overflow:
                data['task_id'] = str(self.task_id)
                self.task_id += 1
                data['ack'] = 0
            else:
                data['ack'] += 1

            data['user_id'] = user_id
            data['node_id'] = node.name
            node.work_number += 1
            data['cur_weight'] = node.cur_weight
            data['status'] = 'work'
            data['schedule'] = 0.0
            data['entry_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.work[data['task_id']] = data
            if not online.observe.get('user' + str(data['user_id'])):
                online.observe['user' + str(data['user_id'])] = list()
            server = xmlrpclib.Server("http://" + node.rpc_address)
            server.add_job(data)
        except Exception as e:
            result['status'] = 500
            result['info'] = str(e)
        return result

    def put_data(self, data, user_id, overflow=False):

        """
        分配任务
        :param data:
        :param user_id:
        :param overflow:
        :return:
        """

        return self.add_job(data, user_id, overflow)

    def get_work_info(self, user_id):

        """
        得到所有给定用户ID的任务状态
        :param user_id:
        :return:
        """

        work = list()
        for key in self.work.keys():
            if self.work[key]['user_id'] == user_id:
                work.append(self.work[key])
        return work

    def check_task_info(self):
        for key in self.keys:
            total = NodeDisPatch.get_task_time_stamp(self.work[key])
            cur = NodeDisPatch.get_cur_time_stamp()
            if cur - total > 5:
                self.work[key]['status'] = 'failed'
                self.work[key]['result'] = "<a>Time out</a>"
                NodeDisPatch.dispatch_info("user" + str(self.work[key]['user_id']), self.work[key])
            if self.can_restart(self.work[key]):
                try:
                    server = xmlrpclib.Server("http://" + online.online_protocol[self.work[key]["node_id"]].rpc_address)
                    d = deferToThread(server.kill_task, key)
                    d.addCallbacks(self.success, self.failed, callbackKeywords=(self.work[key]))  # 分发任务并更新任务
                    d.addCallbacks(self.failed, self.failed)
                except Exception as e:
                    self.put_data(self.work[key], self.work[key]['user_id'], overflow=True)
                    print e, "connect rpc server failed, try run task on other node."
            else:
                pass
            NodeDisPatch.dispatch_info("user" + str(self.work[key]['user_id']), self.work[key])
        reactor.callLater(1, self.check_task_info)

    @staticmethod
    def update_work_info(task, node):
        task['status'] = "work"
        task['ack'] += 1
        task['node_id'] = node.name
        task['entry_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        task['result'] = "<a>Being generated</a>"
        return task

    def can_restart(self, task):
        try:
            if task['ack'] < 3 and self.OnlineProtocol.get_online_protocols("node") and task['status'] == 'failed':
                return True
        except Exception:
            return False

    @staticmethod
    def dispatch_info(user, info):
        task_list = online.get_online_protocols("task")
        for task in task_list:
            if task.div_name == user:
                task.transport.write(json.dumps(info))

    def __getitem__(self, item):

        """
        支持下标直接引用
        :param item:
        :return:
        """

        return self.work.get(item)

    def __getattr__(self, item):

        """
        获取给定属性的值
        :param item:
        :return:
        """

        if item == 'keys':
            return self.work.keys()
        elif item == "next_node":
            return self.get_next_index()

    @staticmethod
    def get_task_time_stamp(task):

        """
        得到任务的时间戳
        :param task:
        :return:
        """

        temp = task['entry_time']
        time_list = time.strptime(temp, '%Y-%m-%d %H:%M:%S')
        return time.mktime(time_list)

    @staticmethod
    def get_task_time_interval(submit, update):

        """
        得到更新时间与提交时间的时间戳
        :param submit:
        :param update:
        :return:
        """

        total = NodeDisPatch.get_task_time_stamp(submit)
        cur = NodeDisPatch.get_task_time_stamp(update)
        return cur - total

    @staticmethod
    def get_cur_time_stamp():

        """
        得到当前时间的时间戳
        :return:
        """

        temp = {"entry_time": datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        return NodeDisPatch.get_task_time_stamp(temp)

    def get(self, item):
        return self.work.get(item)

    def success(self, *args, **kwargs):
        node = self.next_node
        if args[0]['status'] == 200:
            server = xmlrpclib.Server("http://" + node.rpc_address)
            self.work[kwargs['task_id']] = self.update_work_info(kwargs, node)
            server.add_job(kwargs)
            return "add_job to node success to {}".format(node.name)
        else:
            return "job not find, can dispatch to other node"

    @staticmethod
    def failed(*args, **kwargs):
        print args, kwargs


NodeDisPatch = NodeDisPatch()
reactor.callLater(1, NodeDisPatch.check_task_info)
