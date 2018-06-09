# coding=utf-8

from twisted.internet import reactor
from twisted.web import server
from twisted.web.wsgi import WSGIResource
from twisted.python import log
import sys
from webapp import create_app


log.startLogging(sys.stdout)
app = create_app('default')

resource = WSGIResource(reactor, reactor.getThreadPool(), app)
site = server.Site(resource)
reactor.listenTCP(int(app.config['LISTEN_PORT']), site)
reactor.run()
