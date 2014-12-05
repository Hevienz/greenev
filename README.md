greenev
=======

greenev是一个基于greenlet协程，事件驱动，非阻塞socket模型的Python网络库，它使得可以编写同步的代码，却得到异步执行的优点。

greenev is a Python networking library that bseed on greenlet's coroutine, it is event driven and use non-blocking socket model. It makes writing synchronous code gain the advantage of asynchronous execution.

本项目受到gevent, openresty, alilua, skynet, luactor, levent, clowwindy/ssloop的启发，在此表示感谢。

Inspired by gevent, openresty, alilua, skynet, luactor, levent, clowwindy/ssloop, thanks for all of them.

* reactor模式采用基于epoll, kqueue, poll, select的IO复用机制
* 基于底层的reactor完成上层greenlet协程的调度
* 在CentOS6.5, Ubuntu12.04, FreeBSD10.1, Windows7上测试通过

测试前请修改如下系统参数：



net.nf_conntrack_max = 65000

net.netfilter.nf_conntrack_tcp_timeout_established = 1200
