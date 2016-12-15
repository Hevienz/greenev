#coding=utf-8
__all__ = ["coroutine"]


from functools import wraps
from greenlet import greenlet


# 将一个函数封装成协程的装饰器
def coroutine(func):
    @wraps(func)
    def wrapper():
        return greenlet(func)
    return wrapper
