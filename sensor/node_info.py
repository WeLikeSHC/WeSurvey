# encoding=utf-8
import time
import psutil
import socket
import os
from functools import wraps
from twisted.internet.threads import deferToThread


def monitor_timer(function):
    '''
    监控函数的执行时间
    :param function:
    :return:
    '''

    @wraps(function)
    def function_timer(*args, **kwargs):
        t0 = time.time()
        result = function(*args, **kwargs)
        t1 = time.time()
        print 'Total time running %s: %s seconds' % (
            function.func_name, str(t1 - t0))
        return result

    return function_timer


def get_host_ip():
    s = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()
    return ip


def get_net_card():
    info = psutil.net_if_addrs()
    for k, v in info.items():
        for item in v:
            if item[1] == get_host_ip():
                return k
    return ""


class Monitor(object):

    def __init__(self):
        os.system("rm -r -f net.pid")
        os.system("ifstat -i {} > net.pid &".format(get_net_card()))
        self.monitor = dict()
        self.exector()

    @staticmethod
    def delete():
        os.system("rm -r -f net.pid && killall ifstat")

    def print_info(self, *args, **kwargs):
        print args, kwargs

    def exector(self):
        d = deferToThread(self.update)
        d.addCallbacks(self.print_info, self.print_info)

    def update(self):
       while True:
           self. monitor_host()

    def monitor_host(self):

        """
        :return:
        """
        monitor_info = dict()
        free = round(psutil.virtual_memory().free / (1024.0 * 1024.0 * 1024.0), 2)
        total = round(psutil.virtual_memory().total / (1024.0 * 1024.0 * 1024.0), 2)
        monitor_info['memory_total'] = str(total) + "GB"
        monitor_info['memory_use'] = round((total - free) / total, 2)
        monitor_info['cpu_total'] = psutil.cpu_count()
        monitor_info['cpu_use'] = round(psutil.cpu_percent(1) / 100, 2)
        monitor_info['disk_use'] = str(psutil.disk_usage('/').used / 10 ** 9) + "GB"
        monitor_info['disk_total'] = str(psutil.disk_usage('/').total / 10 ** 9) + "GB"
        net_info = os.popen("tail -1 net.pid").read()
        out_command = "echo '%s' | awk '{print $1}'" % (net_info, )
        in_command = "echo '%s' | awk '{print $2}'" % (net_info, )
        monitor_info['network_launch'] = os.popen(in_command).read().strip(" ").strip("\n") + "kb/s"
        monitor_info['network_receive'] = os.popen(out_command).read().strip(" ").strip("\n") + "kb/s"
        self.monitor = monitor_info

    def __getitem__(self, item):
        return self.monitor.get(item)


Monitor = Monitor()
