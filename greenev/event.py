#coding=utf-8
__all__ = ["BaseEventLoop"]


from .reactor import Reactor


class BaseEventLoop(Reactor):
    def __init__(self):
        super(BaseEventLoop, self).__init__()

    # 调度一次协程
    def run_once(self, coro, *args, **kwargs):
        return coro.switch(*args, **kwargs)

    # 调度协程直到完成
    def run_until_complete(self, coro, *args, **kwargs):
        while True:
            result = coro.switch(*args, **kwargs)
            if coro.dead:
                return result
