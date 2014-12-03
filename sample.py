from greenev import Server
import greenlet

class MyServer(Server):
    def handler(self, request, fileno):
        g=greenlet.getcurrent()
        g.parent.switch("Info: ")
        return request

if __name__ == "__main__":
    ser=MyServer(8080)
    ser.start()
