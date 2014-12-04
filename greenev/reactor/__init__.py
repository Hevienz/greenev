import select
import sys

if 'epoll' in select.__dict__:
    from epollreactor import EpollReactor as Reactor
elif 'kqueue' in select.__dict__:
    from kqueuereactor import KqueueReactor as Reactor
elif 'poll' in select.__dict__:
    from pollreactor import PollReactor as Reactor
elif 'select' in select.__dict__:
    from selectreactor import SelectReactor as Reactor
else:
    print "There is no reactor can be used." 
    sys.exit(1)
