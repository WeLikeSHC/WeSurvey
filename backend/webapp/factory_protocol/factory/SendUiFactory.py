# coding=utf-8

from .BaseFactory import BaseFactory


class SendUiFactory(BaseFactory):
    def __init__(self, name=None, protocol=None, host=None):
        BaseFactory.__init__(self, name, protocol, host)
