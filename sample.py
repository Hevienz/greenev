import greenlet
from greenev import coroutine, server
import logging


logging.basicConfig(level=logging.DEBUG)


@coroutine
def handler(C):
    g = greenlet.getcurrent()
    while True:
        print("-------------------")
        try:
            data = C.read()
        except server.NoDataException as e:
            pass
        else:
            print("MSG from %s: %s" % (C.addr, data))
            C.write(b"REPLAY: " + data)
        g.parent.switch()


s = server.StreamServer(("0.0.0.0", 1234), handler)
s.run_forever()
