import unittest
from coroutine import coroutine


class T(unittest.TestCase):
    def setUp(self):
        @coroutine
        def func(arg):
            return arg
        self.coro = func

    def tearDown(self):
        pass

    def test_coroutine(self):
        self.assertEqual(self.coro().switch('ret'), 'ret', 'fail')


if __name__ =='__main__':
    unittest.main()
