import unittest
from coroutine import coroutine
from event import BaseEventLoop
import greenlet


class T(unittest.TestCase):
    def setUp(self):
        @coroutine
        def func(arg):
            print("arg:", arg)
            g = greenlet.getcurrent()
            print("once:", g.parent.switch("once"))
            print("twice:", g.parent.switch("twice"))
            return "ret"
        self.coro = func

        self.loop = BaseEventLoop()

    def tearDown(self):
        pass

    def test_baseeventloop_run_once(self):
        self.assertEqual(self.loop.run_once(self.coro(), "ds"), 'once', 'fail')

    def test_baseeventloop_run_until_complete(self):
        self.assertEqual(self.loop.run_until_complete(self.coro(), "ds"), 'ret', 'fail')


if __name__ =='__main__':
    unittest.main()
