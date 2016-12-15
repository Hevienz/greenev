#coding=utf-8
__all__ = ["Reactor"]


import select


# 根据相应的平台选择相应的Reactor实现
if hasattr(select, "epoll"):
    from .epollreactor import EpollReactor as Reactor
elif hasattr(select, "kqueue"):
    from .kqueuereactor import KqueueReactor as Reactor
elif hasattr(select, "poll"):
    from .pollreactor import PollReactor as Reactor
elif hasattr(select, "select"):
    from .selectreactor import SelectReactor as Reactor
else:
    raise NotImplementedError
