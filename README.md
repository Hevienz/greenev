greenev
=======

greenev是一个基于greenlet协程，事件驱动，非阻塞socket模型的Python服务器框架，它使得可以编写同步的代码，却得到异步执行的优点。

greenev is a Python server framework that bseed on greenlet's coroutine, it is event driven and use non-blocking socket model. It makes writing synchronous code gain the advantage of asynchronous execution.

本项目受到gevent, openresty, alilua, skynet, luactor, levent的启发，在此表示感谢。

Inspired by gevent, openresty, alilua, skynet, luactor, levent, thanks for all of them.

Sample:
---
示例：

from greenev import Server
import greenlet

class MyServer(Server):
    def processRequest(self, request):
        g=greenlet.getcurrent()
        g.parent.switch("Info: ")
        return "My code here.\n"

if __name__ == "__main__":
    ser=MyServer(8080)
    ser.poll()
