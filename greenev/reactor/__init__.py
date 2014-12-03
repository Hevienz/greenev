import select

if 'epoll' in select.__dict__:
    from epollreactor import EpollReactor as Reactor
else:
    from selectreactor import SelectReactor as Reactor
