import platform
import greenlet
_os = platform.system()
if _os == "Linux":
    from greenepoll import EpollServer as Server
else:
    from greenselect import SelectServer as Server
