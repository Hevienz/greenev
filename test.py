from greenev import Server
import greenlet

class MyServer(Server):
    def handler(self, request, fileno):
        print("MSG: ", request)
        return request

if __name__ == "__main__":
    ser=MyServer(1234)
    ser.start()
