from scheduler import Scheduler
import socket

class Server(Scheduler):
    def __init__(self, port):
        super(Server, self).__init__()
        self.sersock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sersock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sersock.bind(('0.0.0.0', port))
        self.sersock.listen(5000)
        self.sersock.setblocking(0)

    def start(self, timeout=10):
        self.sched(self.sersock, timeout)
