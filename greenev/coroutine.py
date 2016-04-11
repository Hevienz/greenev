__all__ = ["coroutine"]


from functools import wraps
from greenlet import greenlet


def coroutine(func):
    @wraps(func)
    def wrapper():
        return greenlet(func)
    return wrapper
