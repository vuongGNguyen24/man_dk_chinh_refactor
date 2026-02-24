import threading
from typing import Callable, List, Union
from .socket_manager import UDPSocketManager


class UDPServer:
    """
    Infrastructure-level UDP event dispatcher
    Singleton-style usage (1 instance shared)
    """

    def __init__(
        self,
        socket_manager: UDPSocketManager,
        buffer_size: int = 4096,
    ):
        self._socket_manager = socket_manager
        self._buffer_size = buffer_size

        self._running = False
        self._thread: Union[threading.Thread, None] = None

        self._subscribers: List[Callable[[bytes, tuple], None]] = []
        self._lock = threading.Lock()

    # ---------- subscription ----------

    def subscribe(self, callback: Callable[[bytes, tuple], None]):
        with self._lock:
            self._subscribers.append(callback)

    # ---------- lifecycle ----------

    def start(self):
        if self._running:
            return

        self._running = True
        sock = self._socket_manager.open()

        def _loop():
            while self._running:
                data, addr = sock.recvfrom(self._buffer_size)

                with self._lock:
                    subscribers = list(self._subscribers)

                for function in subscribers:
                    function(data, addr)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
