__all__ = ["Reactor"]


import select


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
