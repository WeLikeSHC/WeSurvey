# coding=utf-8
from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.internet import reactor

import cgi


class FormPage(Resource):

    """
    twisted 进行处理的函数默认要加上 render_ 前缀
    当请求调用时 把 render_ + 请求方法的名称进行调用
    rpc 也是这个道理
    """

    def render_GET(self, request):
        return '<html><body><form method="POST" action="./form">Name:<input name="the-name" type="text" /> \
        <br />Age:<input name="the-age" type="text" /><br /> \
        <input type="submit" value="submit" /></form></body></html>'

    def render_POST(self, request):
        return '<html><body>You submitted: Name:%s,Age:%s</body></html>' % (cgi.escape(request.args["the-name"][0]),
                                                                         cgi.escape(request.args["the-age"][0]),)


root = Resource()  # 可以访问的资源
root.putChild("form", FormPage())  # 静态地址分发 把自定义的类给定url放入到资源中
factory = Site(root)  # 把资源绑定到对应的工厂
reactor.listenTCP(8880, factory)
reactor.run()
