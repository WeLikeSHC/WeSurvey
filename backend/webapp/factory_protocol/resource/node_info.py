# coding=utf-8
import json
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
from ..dispatch.node_info_dispatch import TaskDispatch


class NodePage(Resource):
    """
    twisted 进行处理的函数默认要加上 render_ 前缀
    当请求调用时 把 render_ + 请求方法的名称进行调用
    rpc 也是这个道理
    """
    def render_POST(self, request):

        content_type_list = request.requestHeaders._rawHeaders.get('content-type', None)
        if content_type_list:
            if content_type_list[0] != 'application/json':
                request.setResponseCode(415)  # Unsupported Media Type
                return "Unsupported Media Type"

        task = request.content.getvalue()
        result = TaskDispatch.dispatch(task)
        if result:
            request.setResponseCode(500)
            return json.dumps(result)
        else:
            request.setResponseCode(200)
        return "ok"


if __name__ == '__main__':
    root = Resource()  # 可以访问的资源
    root.putChild("form", NodePage())  # 静态地址分发 把自定义的类给定url放入到资源中
    factory = Site(root)  # 把资源绑定到对应的工厂
    reactor.listenTCP(8880, factory)
    reactor.run()
