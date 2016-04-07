__all__ = ["Timer"]


import time


class Timer(object):
    def __init__(self, inittime):
        self.inittime = inittime
        self.time = time.time()
        self.deadline = self.inittime + self.time

    def canRun(self):
        return time.time() > self.deadline

    def isTimeout(self):
        return time.time() > self.deadline
