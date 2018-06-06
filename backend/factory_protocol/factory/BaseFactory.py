# -*- coding: utf-8 -*-


from twisted.internet.protocol import Factory


class BaseFactory(Factory):
    def __init__(self, name=None, protocol=None, host=None):
        self.instanceFactoryName = name
        self.protocol = protocol
        self.host = host
        self.numProtocols = 0  # 当前结点数量
        self.OnlineProtocol = None

        print self.instanceFactoryName, 'Server start listening'
        return


if __name__ == '__main__':
    pass
