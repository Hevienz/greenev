#coding=utf-8
__all__ = ["AbstractReactor"]


from abc import ABCMeta, abstractmethod


# 定义Reactor的虚类
class AbstractReactor(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        raise NotImplementedError

    # 虚方法poll阻塞等待读写事件，当有读写事件时，返回一个列表，列表中的每一个元素是一个元组，
    # 元组的第一个元素是文件描述符，第二个元素标识了该文件描述符上的读写事件
    @abstractmethod
    def poll(self, timeout):
        raise NotImplementedError

    # 虚方法register向Reactor注册相应fd上感兴趣的事件
    @abstractmethod
    def register(self, fd, mode):
        raise NotImplementedError

    # 虚方法unregister解除相应fd在Reactor上的注册
    @abstractmethod
    def unregister(self, fd):
        raise NotImplementedError

    # 虚方法modify修改Reador上相应fd感兴趣的事件
    @abstractmethod
    def modify(self, fd, mode):
        raise NotImplementedError
