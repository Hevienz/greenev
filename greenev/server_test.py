import server
from coroutine import coroutine
import greenlet
import logging


logging.basicConfig(level=logging.DEBUG)


@coroutine
def handler(C):
    g = greenlet.getcurrent()
    while True:
        try:
            data = C.read()
        except server.NoDataException as e:
            pass
        else:
            print("MSG:", data)
            C.write(b"REPLAY: " + data)
        g.parent.switch()


s = server.StreamServer(("0.0.0.0", 1234), handler)
s.run_forever()
