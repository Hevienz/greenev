import socket
import select
import greenlet
import time
import errno

class EpollServer(object):
    def __init__(self, port):
        self.sersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sersock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sersock.bind(('0.0.0.0', port))
        self.sersock.listen(5000)
        self.sersock.setblocking(0)

    def processRequest(self, request, fileno):
        g=greenlet.getcurrent()
        g.parent.switch("Warning: ")
        return "Replace processRequest function in your code.\n"

    def sleep(self, seconds, fileno, coroutine):
        self.run_tasks[fileno]["delay"] = seconds + time.time()
        coroutine.parent.switch()

    def poll(self, timeout=10):
        epoll = select.epoll()
        epoll.register(self.sersock.fileno(), select.EPOLLIN |select.EPOLLHUP | select.EPOLLERR | select.EPOLLET)

        try:
            conns = {}
            self.run_tasks = {}

            while True:
                for (fileno, task_t) in self.run_tasks.items():
                    if time.time() > self.run_tasks[fileno]["delay"]:
                        res = task_t["task"].switch(conns[fileno]["req"], fileno)
                        if type(res) is str:
                            conns[fileno]["resp"] += res
                    if task_t["timeout"] and task_t["timeout"] < time.time():
                        conns[fileno]["resp"] = "Timeout"
                        del self.run_tasks[fileno]

                events = epoll.poll(1)
                for fileno, event in events:
                    if fileno == self.sersock.fileno():
                        try:
                            while True:
                                clisock, cliaddr = self.sersock.accept()
                                clisock.setblocking(0)
                                epoll.register(clisock.fileno(), select.EPOLLIN | select.EPOLLET)
                                conns[clisock.fileno()] = {}
                                conns[clisock.fileno()]["sock"] = clisock
                                conns[clisock.fileno()]["req"] = b''
                                conns[clisock.fileno()]["resp"] = b''
                                epoll.modify(fileno, select.EPOLLIN | select.EPOLLET)
                        except socket.error as e:
                            if e.errno == errno.EAGAIN: pass
                            else: print e
                    elif event & (select.EPOLLHUP | select.EPOLLERR):
                        epoll.unregister(fileno)
                        conns[fileno]["sock"].close()
                        del conns[fileno]
                        try:
                            del self.run_tasks[fileno]
                        except:
                            pass
                    elif event & select.EPOLLIN:
                        while True:
                            try:
                                buf = conns[fileno]["sock"].recv(4096)
                                conns[fileno]["req"] += buf
                                if len(buf) < 4096: raise socket.error("recv < 4096")
                            except socket.error as e:
                                task_t = {"task": greenlet.greenlet(self.processRequest),
                                          "timeout": None,
                                          "delay": None,}
                                if timeout >= 0:
                                    task_t["timeout"] = time.time() + timeout
                                else:
                                    pass
                                self.run_tasks[fileno] = task_t
                                epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                                break
                    elif event & select.EPOLLOUT:
                        try:
                            while len(conns[fileno]["resp"]) > 0:
                                nsend = conns[fileno]["sock"].send(conns[fileno]["resp"])
                                conns[fileno]["resp"] = conns[fileno]["resp"][nsend:]
                        except socket.error:
                            pass
                        if len(conns[fileno]["resp"]) == 0:
                            if fileno not in self.run_tasks:
                                epoll.unregister(fileno)
                                conns[fileno]["sock"].close()
                            elif self.run_tasks[fileno]["task"].dead:
                                del self.run_tasks[fileno]
                                epoll.unregister(fileno)
                                conns[fileno]["sock"].close()
                            else:
                                epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)

        finally:
            epoll.unregister(self.sersock.fileno())
            epoll.close()
            self.sersock.close()
