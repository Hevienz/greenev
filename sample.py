from greenev import Server
import greenlet
import time

class MyServer(Server):
    def processRequest(self, request, fileno):
        g=greenlet.getcurrent()
        g.parent.switch("Info: ")
        g.parent.switch("my code here.")
        g.parent.switch("!!!!!!!!!!!!!!")


if __name__ == "__main__":
    ser=MyServer(8080)
    ser.poll(timeout=10)
