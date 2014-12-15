greenev
=======

greenev是一个基于greenlet协程，事件驱动，非阻塞socket模型的Python网络服务框架，它使得可以编写同步的代码，却得到异步执行的优点。

greenev is a Python networking service framework that bseed on greenlet's coroutine, it is event driven and use non-blocking socket model. It makes writing synchronous code gain the advantage of asynchronous execution.

本项目受到gevent, openresty, alilua, skynet, clowwindy/ssloop的启发，在此表示感谢。

Inspired by gevent, openresty, alilua, skynet, clowwindy/ssloop, thanks for all of them.

* reactor模式采用基于epoll, kqueue, poll, select的IO复用机制
* 基于底层的reactor完成上层greenlet协程的调度
* 在CentOS6.5, Ubuntu12.04, FreeBSD10.1, Windows7上测试通过
* 只需调用g.parent.switch挂起当前的协程，而无需管理其中的细节

测试前请修改如下系统参数(CentOS)：

```
net.ipv4.tcp_syncookies = 1 
net.ipv4.tcp_tw_reuse = 1 
net.ipv4.tcp_tw_recycle = 1 
net.ipv4.tcp_fin_timeout = 30 
net.ipv4.tcp_keepalive_time = 1200 
net.ipv4.ip_local_port_range = 1024 65000 
net.ipv4.tcp_max_syn_backlog = 8192 
fs.file-max=65535 
net.ipv4.tcp_max_tw_buckets = 20000 
net.nf_conntrack_max = 65000 
net.netfilter.nf_conntrack_tcp_timeout_established = 1200
```
