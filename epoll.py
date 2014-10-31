import socket
import select
import greenlet

def processRequest(request):
    g=greenlet.getcurrent()
    g.parent.switch("ds\n")
    g.parent.switch("zzz\n")
    return "i love you\n"

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
serversocket.bind(('0.0.0.0', 8080))
serversocket.listen(1)
serversocket.setblocking(0)

epoll = select.epoll()
epoll.register(serversocket.fileno(), select.EPOLLIN | select.EPOLLET)

try:
    run_tasks={}

    connections = {}
    requests = {}
    responses = {}

    while True:

        for (fileno, task) in run_tasks.items():
             res = task.switch(requests[fileno])
             responses[fileno] += res

        events = epoll.poll(1)
        #print events
        for fileno, event in events:
            if fileno == serversocket.fileno():
                try:
                    while True:
                        connection, address = serversocket.accept()
                        connection.setblocking(0)
                        epoll.register(connection.fileno(), select.EPOLLIN | select.EPOLLET)
                        connections[connection.fileno()] = connection
                        requests[connection.fileno()] = b''
                        responses[connection.fileno()] = b''
                except socket.error:
                    pass
            elif event & select.EPOLLIN:
                while True:
                    try:
                         requests[fileno] += connections[fileno].recv(1024)
                    except socket.error as e:
                         run_tasks[fileno]=greenlet.greenlet(processRequest)
                         epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
                         break
            elif event & select.EPOLLOUT:
                try:
                    while len(responses[fileno]) > 0:
                        byteswritten = connections[fileno].send(responses[fileno])
                        responses[fileno] = responses[fileno][byteswritten:]
                except socket.error:
                    pass
                if len(responses[fileno]) == 0:
                    if run_tasks[fileno].dead:
                        del run_tasks[fileno]
                        epoll.modify(fileno, select.EPOLLET)
                        connections[fileno].shutdown(socket.SHUT_RDWR)
                    else:
                        epoll.modify(fileno, select.EPOLLOUT | select.EPOLLET)
            elif event & select.EPOLLHUP:
                epoll.unregister(fileno)
                connections[fileno].close()
                del connections[fileno]
finally:
    epoll.unregister(serversocket.fileno())
    epoll.close()
    serversocket.close()
