import select

if 'epoll' in select.__dict__:
    from epollreactor import EpollReactor as Reactor
elif 'poll' in select.__dict__:
    from pollreactor import PollReactor as Reactor
else:
    from selectreactor import SelectReactor as Reactor
