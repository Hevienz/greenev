import select
from collections import defaultdict

MAX_EVENTS = 1024

class KqueueReactor(object):
    EV_NULL = 0x00
    EV_DISCONNECTED = 0x18
    EV_IN = 0x01
    EV_OUT = 0x04

    def __init__(self):
        self._poller = select.kqueue()
        self._fds = {}

    def _control(self, fd, mode, flags):
        events = []
        if mode & self.EV_IN:
            events.append(select.kevent(fd, select.KQ_FILTER_READ, flags))
        if mode & self.EV_OUT:
            events.append(select.kevent(fd, select.KQ_FILTER_WRITE, flags))
        for e in events:
            self._poller.control([e], 0)

    def _poll(self, timeout):
        if timeout < 0:
            timeout = None  # kqueue behaviour
        events = self._poller.control(None, MAX_EVENTS, timeout)
        results = defaultdict(lambda: self.EV_NULL)
        for e in events:
            fd = e.ident
            if e.filter == select.KQ_FILTER_READ:
                results[fd] |= self.EV_IN
            elif e.filter == select.KQ_FILTER_WRITE:
                results[fd] |= self.EV_OUT
        return results.iteritems()

    def _add_fd(self, fd, mode):
        self._fds[fd] = mode
        self._control(fd, mode, select.KQ_EV_ADD)

    def _remove_fd(self, fd):
        self._control(fd, self._fds[fd], select.KQ_EV_DELETE)
        del self._fds[fd]

    def _modify_fd(self, fd, mode):
        self._remove_fd(fd)
        self._add_fd(fd, mode)
