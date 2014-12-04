from reactor import Reactor
import greenlet
import errno
import socket
from timer import Timer

class Scheduler(Reactor):
    def __init__(self):
        super(Scheduler, self).__init__()
        self.conns = {}
        self.run_tasks = {}

    def _init_conns(self, fd, sock):
        self.conns[fd] = {}
        self.conns[fd]["sock"] = sock
        self.conns[fd]["req"] = b''
        self.conns[fd]["resp"] = b''

    def _init_run_tasks(self, fd, timeout):
        task_t = {"task": greenlet.greenlet(self.handler),
                  "timeout": None,
                  "delay": None,}
        if timeout >= 0:
            task_t["timeout"] = Timer(timeout)
        else:
            pass
        self.run_tasks[fd] = task_t

    def _clear_all(self, fd):
        if fd in self.conns: del self.conns[fd]
        if fd in self.run_tasks: del self.run_tasks[fd]

    def sleep(self, seconds, fileno, coroutine):
        self.run_tasks[fileno]["delay"] = Timer(seconds)
        coroutine.parent.switch()

    def handler(self, request, fileno):
        g=greenlet.getcurrent()
        g.parent.switch("Warning: ")
        return "Replace processRequest function in your code.\n"

    def _sched_coroutine(self):
        for (fileno, task_t) in self.run_tasks.items():
            if task_t["delay"] is None or task_t["delay"].canRun():
                res = task_t["task"].switch(self.conns[fileno]["req"], fileno)
                if type(res) is str:
                    self.conns[fileno]["resp"] += res
            if (not task_t["timeout"] is None) and task_t["timeout"].isTimeout():
                self.conns[fileno]["resp"] = "Timeout"
                del self.run_tasks[fileno]

    def sched(self, sersock, timeout=10):
        serfd = sersock.fileno()
        self.register(serfd, self.EV_IN)

        while True:
            self._sched_coroutine()

            events = self.poll(1)
            for fileno, event in events:
                if fileno == serfd:
                    try:
                        while True:
                            clisock, cliaddr = sersock.accept()
                            clifd = clisock.fileno()
                            clisock.setblocking(0)
                            self.register(clifd, self.EV_IN)
                            self._init_conns(clifd, clisock)
                    except socket.error as e:
                        if e.errno == errno.EAGAIN:
                            self.modify(serfd, self.EV_IN)
                        else:
                            print e
                elif event & self.EV_DISCONNECTED:
                    self.unregister(fileno)
                    self.conns[fileno]["sock"].close()
                    self._clear_all(fileno)
                elif event & self.EV_IN:
                    while True:
                        try:
                            buf = self.conns[fileno]["sock"].recv(4096)
                            self.conns[fileno]["req"] += buf
                            if len(buf) < 4096: raise socket.error("recv < 4096")
                        except socket.error as e:
                            self._init_run_tasks(fileno, timeout)
                            self.modify(fileno, self.EV_OUT)
                            break
                elif event & self.EV_OUT:
                    try:
                        while len(self.conns[fileno]["resp"]) > 0:
                            nsend = self.conns[fileno]["sock"].send(self.conns[fileno]["resp"])
                            self.conns[fileno]["resp"] = self.conns[fileno]["resp"][nsend:]
                    except socket.error:
                        pass
                    if len(self.conns[fileno]["resp"]) == 0:
                        if fileno not in self.run_tasks:
                            self.unregister(fileno)
                            self.conns[fileno]["sock"].close()
                        elif self.run_tasks[fileno]["task"].dead:
                            self.unregister(fileno)
                            self.conns[fileno]["sock"].close()
                            self._clear_all(fileno)
                        else:
                            self.modify(fileno, self.EV_OUT)

