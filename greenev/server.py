__all__ = ["StreamServer", "NoDataException"]


import socket
import errno
import logging
try:
    import queue
except ImportError:
    import Queue as queue
from .event import BaseEventLoop


if not hasattr(__builtins__, "BlockingIOError"):
    BlockingIOError = socket.error


BUFSIZE = 4096


class NoDataException(Exception):
    pass


class Client(object):
    _canRead = False
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
        closed = False

        data = b''
        try:
            while True:
                buf = self._recv(BUFSIZE)
                logging.debug("buf[%d]: %s" % (len(buf), buf))
                if len(buf) == 0:
                    logging.info("The other side closed.")
                    closed = True
                    break
                elif len(buf) < BUFSIZE:
                    data += buf
                    break
                elif len(buf) == BUFSIZE:
                    data += buf
        except BlockingIOError as e:
            if e.errno == errno.EAGAIN:
                pass
            else:
                logging.exception(e)
        except Exception as e:
            logging.exception(e)

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
        try:
            return self._recv_queue.get_nowait()
        except queue.Empty as e:
            self._canRead = False
            raise NoDataException

    def write(self, data):
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

    def _filenoToClient(self, fileno):
        return self._sock_mapping[fileno]

    def _clear_Client(self, fileno):
        self.unregister(fileno)
        C = self._filenoToClient(fileno)
        del C
        del self._sock_mapping[fileno]
        del self._task_mapping[fileno]


    def _sched_coroutine(self):
        for (fileno, coro) in self._task_mapping.items():
            C = self._filenoToClient(fileno)
            if C._canRead or C._needWrite:
                coro.switch(C)

                if coro.dead:
                    self._clear_Client(C)

    def run_forever(self):
        self.register(self._lisenerfd, self.EV_IN)

        while True:
            self._sched_coroutine()

            events = self.poll(1)
            for fileno, event in events:
                if fileno == self._lisenerfd:
                    try:
                        while True:
                            clisock, cliaddr = self._lisener.accept()
                            clifd = clisock.fileno()
                            clisock.setblocking(0)
                            self.register(clifd, self.EV_IN | self.EV_OUT)
                            self._sock_mapping[clifd] = Client(clisock, cliaddr)
                            self._task_mapping[clifd] = self._handler()
                    except BlockingIOError as e:
                        if e.errno == errno.EAGAIN:
                            self.modify(self._lisenerfd, self.EV_IN)
                        else:
                            logging.exception(e)
                    except Exception as e:
                        logging.exception(e)

                elif event & self.EV_DISCONNECTED:
                    self._clear_Client(fileno)

                elif event & self.EV_IN:
                    C = self._filenoToClient(fileno)

                    if C._recv_and_cache_data():
                        self._clear_Client(fileno)
                    else:
                        self.modify(fileno, self.EV_IN | self.EV_OUT)

                elif event & self.EV_OUT:
                    C = self._filenoToClient(fileno)

                    if C._send_cache_data_to_socket():
                        self._clear_Client(fileno)
                    else:
                        self.modify(fileno, self.EV_IN | self.EV_OUT)
