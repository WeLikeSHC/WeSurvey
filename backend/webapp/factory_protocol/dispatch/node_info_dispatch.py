# coding=utf-8

from job_dispatch import NodeDisPatch
import json


class TaskDispatch:

    def __init__(self):
        self.info_status = {"failed": ["<a>Generation failure</a>", "<a>More than the maximum retrial times</a>",
                                       "<a>no slave</a>", "<a>Time out</a>"], "work": ['<a>Being generated</a>'],
                            "finish": ['<a>click to download</a>']}
        self.OnlineProtocol = None

    def dispatch(self, task):
        result = dict()

        try:
            task = json.loads(task)
            self.info_check(task)
            NodeDisPatch.work[task['task_id']] = task
            for observe in self.OnlineProtocol.observe.get('user' + str(task['user_id'])):
                observe.transport.write(json.dumps(task))
        except Exception as e:
            result['info'] = str(e)
            print e, "dispatch error"
            return result

    def info_check(self, task):

        if not NodeDisPatch.get(task.get('task_id')):
            raise Exception("task not find!")

        if task['result'] not in self.info_status[task['status']]:
            raise Exception("you send state is {}, but the result is {}".format(task['status'], task['result']))

        if task['node_id'] != NodeDisPatch[task['task_id']]['node_id']:
            raise Exception("You have no right to update this task!")

        interval = NodeDisPatch.get_task_time_interval(NodeDisPatch[task['task_id']], task)

        if interval > 20:
            raise Exception("time out, task submit time is{}, but the current update time is {}".
                            format(NodeDisPatch[task['task_id']]['entry_time'], task['entry_time']))


TaskDispatch = TaskDispatch()
