from greenev import Server
import greenlet
import time

class MyServer(Server):
    def processRequest(self, request):
        g=greenlet.getcurrent()
        g.parent.switch("Info: ")
        return "My code here.\n"

if __name__ == "__main__":
    ser=MyServer(8080)
    ser.poll(timeout=0.0001)
