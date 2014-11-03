import platform
import greenlet
_os = platform.system()
if _os == "Linux":
    from greenepoll import EpollServer as Server
else:
    from greenselect import SelectServer as Server

if __name__ == "__main__":
    class MyServer(Server):
        def processRequest(self, request):
            g=greenlet.getcurrent()
            g.parent.switch("Info: ")
            return "My code here.\n"

    ser=MyServer(8080)
    ser.poll()
