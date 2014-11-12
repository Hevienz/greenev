import socket
import select
import greenlet
import time

class EpollServer(object):
    def __init__(self, port):
        self.sersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sersock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sersock.bind(('0.0.0.0', port))
        self.sersock.listen(5000)
        self.sersock.setblocking(0)

    def processRequest(self, request):
        g=greenlet.getcurrent()
        g.parent.switch("Warning: ")
        return "Replace processRequest function in your code.\n"

    def poll(self, timeout=10):
        epoll = select.epoll()
        epoll.register(self.sersock.fileno(), select.EPOLLIN | select.EPOLLET)

        try:
            conns = {}
            run_tasks = {}

            while True:
                for (fileno, task_t) in run_tasks.items():
                    res = task_t["task"].switch(conns[fileno]["req"])
                    if type(res) is str:
                        conns[fileno]["resp"] += res
                    if task_t["intime"] and task_t["intime"] < time.time():
                        conns[fileno]["resp"] = "Timeout"
                        del run_tasks[fileno]

                events = epoll.poll(1)
                #print events
                for fileno, event in events:
                    if fileno == self.sersock.fileno():
                        try:
                            while True:
                                clisock, cliaddr = self.sersock.accept()
                                #connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
                                clisock.setblocking(0)
                                epoll.register(clisock.fileno(), select.EPOLLIN | select.EPOLLET)
                                conns[clisock.fileno()] = {}
                                conns[clisock.fileno()]["sock"] = clisock
                                conns[clisock.fileno()]["req"] = b''
                                conns[clisock.fileno()]["resp"] = b''
                        except socket.error:
                            pass
                    elif event & select.EPOLLIN:
                        while True:
                            try:
                                conns[fileno]["req"] += conns[fileno]["sock"].recv(1024)
                            except socket.error as e:
                                task_t = {"task": greenlet.greenlet(self.processRequest),
                                          "intime": None,}
                                if timeout >= 0:
                                    task_t["intime"] = time.time() + timeout
                                else:
                                    pass
                                #conns[fileno]["task_status"] = "suspend"
                                run_tasks[fileno] = task_t
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
                            if fileno not in run_tasks:
                                epoll.modify(fileno, select.EPOLLET)
                                conns[fileno]["sock"].shutdown(socket.SHUT_RDWR)
                            elif run_tasks[fileno]["task"].dead:
                                del run_tasks[fileno]
                                epoll.modify(fileno, select.EPOLLET)
                                conns[fileno]["sock"].shutdown(socket.SHUT_RDWR)
                            else:
                                epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                    elif event & select.EPOLLHUP:
                        epoll.unregister(fileno)
                        conns[fileno]["sock"].close()
                        del conns[fileno]
        finally:
            epoll.unregister(self.sersock.fileno())
            epoll.close()
            self.sersock.close()
