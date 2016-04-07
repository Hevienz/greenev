__all__ = ["AbstractReactor"]


from abc import ABCMeta, abstractmethod


class AbstractReactor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    @abstractmethod
    def poll(self, timeout):
        raise NotImplementedError

    @abstractmethod
    def register(self, fd, mode):
        raise NotImplementedError

    @abstractmethod
    def unregister(self, fd):
        raise NotImplementedError

    @abstractmethod
    def modify(self, fd, mode):
        raise NotImplementedError
