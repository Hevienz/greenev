__all__ = ["EpollReactor"]


from .abstractreactor import AbstractReactor
from select import epoll, EPOLLHUP, EPOLLERR, EPOLLIN, EPOLLOUT, EPOLLET


class EpollReactor(AbstractReactor):
    EV_DISCONNECTED = (EPOLLHUP | EPOLLERR)
    EV_IN = EPOLLIN | EPOLLET
    EV_OUT = EPOLLOUT | EPOLLET

    def __init__(self):
        self._poller = epoll()

    def poll(self, timeout):
        return self._poller.poll(timeout)

    def register(self, fd, mode):
        self._poller.register(fd, mode)

    def unregister(self, fd):
        self._poller.unregister(fd)

    def modify(self, fd, mode):
        self._poller.modify(fd, mode)
