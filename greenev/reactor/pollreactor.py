#!/usr/bin/python
from select import poll, POLLHUP, POLLERR, POLLIN, POLLOUT

class PollReactor(object):
    EV_DISCONNECTED = (POLLHUP | POLLERR)
    EV_IN = POLLIN
    EV_OUT = POLLOUT

    def __init__(self):
        self._poller = poll()

    def poll(self, timeout):
        return self._poller.poll(timeout)

    def register(self, fd, mode):
        self._poller.register(fd, mode)

    def unregister(self, fd):
        self._poller.unregister(fd)

    def modify(self, fd, mode):
        self._poller.modify(fd, mode)
