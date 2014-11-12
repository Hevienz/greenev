import select
import socket
import greenlet
import time

class SelectServer(object):
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
        conns = {}
        run_tasks = {}

        insocks = [self.sersock,]
        outsocks = []

        while True:
            for (fileno, task_t) in run_tasks.items():
                res = task_t["task"].switch(conns[fileno]["req"])
                if type(res) is str:
                    conns[fileno]["resp"] += res
                if task_t["intime"] and task_t["intime"] < time.time():
                    conns[fileno]["resp"] = "Timeout"
                    del run_tasks[fileno]

            readable , writable , exceptional = select.select(insocks, outsocks, insocks, 1)
            for s in readable :
                if s is self.sersock:
                    try:
                        while True:
                            clisock, cliaddr = s.accept()
                            clisock.setblocking(0)
                            insocks.append(clisock)
                            conns[clisock.fileno()] = {}
                            conns[clisock.fileno()]["sock"] = clisock
                            conns[clisock.fileno()]["req"] = b""
                            conns[clisock.fileno()]["resp"] = b""
                    except socket.error:
                        pass
                else:
                    while True:
                        try:
                            conns[s.fileno()]["req"] += s.recv(1024)
                        except socket.error as e:
                            task_t = {"task": greenlet.greenlet(self.processRequest),
                                      "intime": None,}
                            if timeout >= 0:
                                task_t["intime"] = time.time() + timeout
                            else:
                                pass
                            run_tasks[s.fileno()] = task_t
                            insocks.remove(s)
                            outsocks.append(s)
                            break
            for s in writable:
                try:
                    while len(conns[s.fileno()]["resp"]) > 0:
                        nsend = s.send(conns[s.fileno()]["resp"])
                        conns[s.fileno()]["resp"] = conns[s.fileno()]["resp"][nsend:]
                except socket.error:
                    pass
                if len(conns[s.fileno()]["resp"]) == 0:
                    if fileno not in run_tasks:
                        outsocks.remove(s)
                        s.shutdown(socket.SHUT_RDWR)
                    elif run_tasks[s.fileno()]["task"].dead:
                        del run_tasks[s.fileno()]
                        outsocks.remove(s)
                        s.shutdown(socket.SHUT_RDWR)
                    else:
                        pass
            for s in exceptional:
                if s in insocks:
                    insocks.remove(s)
                if s in outsocks:
                    outsocks.remove(s)
                s.close()
