__all__ = ["SelectReactor"]


from .abstractreactor import AbstractReactor
from select import select
from collections import defaultdict


class SelectReactor(AbstractReactor):
    EV_NULL = 0x00
    EV_DISCONNECTED = 0x18
    EV_IN = 0x01
    EV_OUT = 0x04

    def __init__(self):
        self._r_list = set()
        self._w_list = set()
        self._x_list = set()

    def poll(self, timeout):
        r, w, x = select(self._r_list, self._w_list, self._x_list, timeout)
        results = defaultdict(lambda: self.EV_NULL)
        for p in [(r, self.EV_IN), (w, self.EV_OUT), (x, self.EV_DISCONNECTED)]:
            for fd in p[0]:
                results[fd] |= p[1]
        return results.items()

    def register(self, fd, mode):
        if mode & self.EV_IN:
            self._r_list.add(fd)
        if mode & self.EV_OUT:
            self._w_list.add(fd)
        self._x_list.add(fd)

    def unregister(self, fd):
        if fd in self._r_list:
            self._r_list.remove(fd)
        if fd in self._w_list:
            self._w_list.remove(fd)
        if fd in self._x_list:
            self._x_list.remove(fd)

    def modify(self, fd, mode):
        self.unregister(fd)
        self.register(fd, mode)
