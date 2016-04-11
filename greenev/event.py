__all__ = ["BaseEventLoop"]


import logging
import errno
import socket
import greenlet
from .reactor import Reactor


class BaseEventLoop(Reactor):
    def __init__(self):
        super(BaseEventLoop, self).__init__()

    def run_once(self, coro, *args, **kwargs):
        return coro.switch(*args, **kwargs)

    def run_until_complete(self, coro, *args, **kwargs):
        while True:
            result = coro.switch(*args, **kwargs)
            if coro.dead:
                return result

