# coding=utf-8

"""
实现任务的分发
"""

from .. onlineProtocol import online
import xmlrpclib
import datetime


class NodeDisPatch:

    def __init__(self):
        self.task_id = 0
        self.work = list()

    @staticmethod
    def get_next_index(node_list):  # 先找到权重最大的结点分配给其任务 然后降低其权重

        total = 0
        _index = -1
        for _i in range(len(node_list)):
            node_list[_i].cur_weight += node_list[_i].weight
            total += node_list[_i].weight
            if _index == -1 or node_list[_index].cur_weight < node_list[_i].cur_weight:
                _index = _i

        node_list[_index].cur_weight -= total
        return node_list[_index]

    def put_data(self, data):
        node_list = online.get_online_protocols("node")
        node = self.get_next_index(node_list)
        if node:
            try: 
                server = xmlrpclib.Server("http://" + node.rpc_address)
                data['task_id'] = self.task_id + 1
                self.task_id +=  1
                data['node_id'] = node.id
                data['status'] = 'work'
                data['schedule'] = 0.0
                data['entry_time'] = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.work.append(data)
                server.add_job(data)
                return {'status': 200}
            except Exception as e:
                return {'status': 500, 'info': str(e)}
        else:
            return {'status': 500, 'info': 'no slave can work!'}
