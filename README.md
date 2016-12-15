# greenev

## Installation
> pip install greenev

## Use case
```python
#coding=utf-8
import greenlet
from greenev import coroutine, server
import logging


logging.basicConfig(level=logging.DEBUG)
LISTEN_ADDR = ("0.0.0.0", 1234)


# 封装handler为协程
@coroutine
# 参数C是一个greenev.Client的对象
def handler(C):
    # 获取协程自己
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
        # 调度回父协程，详见https://greenlet.readthedocs.io/en/latest/#parents
        g.parent.switch()


s = server.StreamServer(LISTEN_ADDR, handler)
logging.info("Listening on %s ..." % (LISTEN_ADDR,))
s.run_forever()

```
