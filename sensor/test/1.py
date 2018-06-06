from twisted.internet.defer import Deferred
from twisted.python.failure import Failure

def got_poem(res):
    print 'Your poem is serverd'
    print res
    #raise Exception('failed')


def poem_failed(err):
    print err.__class__
    print 'No poetry for you'


d = Deferred()

d.addCallbacks(got_poem, poem_failed)
d.addCallbacks(got_poem, poem_failed)
# d.callback('asdasdadadas')
d.callback('i will failed')
print 'finish'
