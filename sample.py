import greenlet
from greenev import coroutine, server


@coroutine
def handler(C):
    g = greenlet.getcurrent()
    while True:
        try:
            data = C.read()
        except server.NoDataException as e:
            pass
        else:
            print("MSG from %s: %s" % (C.addr, data))
            C.write(b"REPLAY: " + data)
            C.close()
        g.parent.switch()


s = server.StreamServer(("0.0.0.0", 1234), handler)
s.run_forever()
