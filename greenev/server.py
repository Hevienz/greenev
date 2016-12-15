#coding=utf-8
__all__ = ["StreamServer", "NoDataException"]


import socket
import errno
import logging
# 解决兼容问题
try:
    import queue
except ImportError:
    import Queue as queue
from .event import BaseEventLoop
# 解决兼容问题
if not hasattr(__builtins__, "BlockingIOError"):
    BlockingIOError = socket.error


BUFSIZE = 4096


class NoDataException(Exception):
    pass


class Client(object):
    # 标识Client是否可读
    _canRead = False
    # 标识Client是否有数据需要写入socket
    _needWrite = False

    def __init__(self, sock, addr):
        self._recv_queue = queue.Queue()
        self._send_queue = queue.Queue()
        self.sock = sock
        self.addr = addr

    def __del__(self):
        self.close()

    def _recv(self, bufsize):
        return self.sock.recv(bufsize)

    def _sendall(self, bytes):
        return self.sock.sendall(bytes)

    def _recv_and_cache_data(self):
        # 标识Client是否关闭
        closed = False

        data = b''
        try:
            while True:
                buf = self._recv(BUFSIZE)
                logging.debug("{%s} buf[%d]: %s" % (self.addr, len(buf), buf))
                # 接收到的数据长度为0，表示连接已关闭
                if len(buf) == 0:
                    logging.info("{%s} The other side closed." % (self.addr,))
                    closed = True
                    break
                # 接收到的数据长度小于BUFSIZE说明暂无数据可以接收
                elif len(buf) < BUFSIZE:
                    data += buf
                    break
                # 接收到的数据长度等于BUFSIZE，可以继续接收，直到接收的数据长度小于BUFSIZE或者遇到EAGAIN
                elif len(buf) == BUFSIZE:
                    data += buf
        except BlockingIOError as e:
            if e.errno == errno.EAGAIN:
                pass
            else:
                logging.exception(e)
        except Exception as e:
            logging.exception(e)

        # 如果接收到数据，将数据丢到接收队列中，并置可读标志为True
        if data:
            try:
                self._recv_queue.put_nowait(data)
            except queue.Full as e:
                logging.exception(e)
            except Exception as e:
                logging.exception(e)
            else:
                self._canRead = True

        return closed

    def _send_cache_data_to_socket(self):
        # 从发送队列获取数据并从相应的socket发出，直到队列为空
        try:
            while True:
                data = self._send_queue.get_nowait()
                self._sendall(data)
        except queue.Empty as e:
            self._needWrite = False
        except Exception as e:
            logging.exception(e)
            return True

        return False

    def read(self):
        # 从接收队列获取数据，当队列为空，置可读标识为False，并引发NoDataException
        try:
            return self._recv_queue.get_nowait()
        except queue.Empty as e:
            self._canRead = False
            raise NoDataException

    def write(self, data):
        # 将数据写入发送队列，并置需要写标识为True
        try:
            ret = self._send_queue.put_nowait(data)
        except queue.Full as e:
            logging.exception(e)
        except Exception as e:
            logging.exception(e)
        else:
            self._needWrite = True

        return ret

    def close(self):
        return self.sock.close()


class StreamServer(BaseEventLoop):
    _backlog = 256
    _sock_mapping = {}
    _task_mapping = {}

    def __init__(self, addr, handle_client):
        super(StreamServer, self).__init__()
        self._lisener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._lisener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._lisener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        self._lisener.bind(addr)
        self._lisener.listen(self._backlog)
        self._lisener.setblocking(0)
        self._lisenerfd = self._lisener.fileno()
        self._handler = handle_client

    # 找到对应fd的Client
    def _filenoToClient(self, fileno):
        return self._sock_mapping[fileno]

    # 清理相应的Client
    def _clear_Client(self, fileno):
        self.unregister(fileno)
        C = self._filenoToClient(fileno)
        del C
        del self._sock_mapping[fileno]
        del self._task_mapping[fileno]

    # 找到所有需要调度的协程，如果其对应的Client的_canRead或_needWrite为True，则调度它，
    # 如果协程已调度完成，清理相应的Client
    def _sched_coroutine(self):
        for (fileno, coro) in self._task_mapping.items():
            C = self._filenoToClient(fileno)
            if C._canRead or C._needWrite:
                coro.switch(C)

                if coro.dead:
                    self._clear_Client(C)

    def run_forever(self):
        # 注册监听fd的可读事件为感兴趣事件
        self.register(self._lisenerfd, self.EV_IN)

        while True:
            # 调度协程
            self._sched_coroutine()

            events = self.poll(1)
            for fileno, event in events:
                # 当fileno为监听fd时，说明有Client连接到服务器端，应尝试accept直到EAGAIN
                if fileno == self._lisenerfd:
                    try:
                        while True:
                            clisock, cliaddr = self._lisener.accept()
                            clifd = clisock.fileno()
                            clisock.setblocking(0)
                            # 注册客户端fd的读写事件为感兴趣事件
                            self.register(clifd, self.EV_IN | self.EV_OUT)
                            self._sock_mapping[clifd] = Client(clisock, cliaddr)
                            # 将协程放入调度池
                            self._task_mapping[clifd] = self._handler()
                            logging.info("{%s} Client connect to server." % (cliaddr,))
                    except BlockingIOError as e:
                        if e.errno == errno.EAGAIN:
                            # 继续设置监听fd的可读事件为感兴趣事件
                            self.modify(self._lisenerfd, self.EV_IN)
                        else:
                            logging.exception(e)
                    except Exception as e:
                        logging.exception(e)

                # 当相应fd挂起或错误时，清理相应的Client
                elif event & self.EV_DISCONNECTED:
                    self._clear_Client(fileno)

                # 当相应fd上有可读事件，从socket中读取数据并放入Client的接收队列
                elif event & self.EV_IN:
                    C = self._filenoToClient(fileno)

                    # 当_recv_and_cache_data返回True时表明相应的socket已关闭，此时将清理相应的Client
                    if C._recv_and_cache_data():
                        self._clear_Client(fileno)
                    else:
                        # 当socket未关闭，继续设置相应fd的读写事件为感兴趣事件
                        self.modify(fileno, self.EV_IN | self.EV_OUT)

                # 当相应fd上有可写事件，从Client的发送队列获取数据并将其从相应的socket上发送出去
                elif event & self.EV_OUT:
                    C = self._filenoToClient(fileno)

                    # 当_send_cache_data_to_socket返回True时，说明从Client的发送队列获取数据异常，此时将清理相应的Client
                    if C._send_cache_data_to_socket():
                        self._clear_Client(fileno)
                    else:
                        # 否则，继续设置相应fd的读写事件为感兴趣事件
                        self.modify(fileno, self.EV_IN | self.EV_OUT)
