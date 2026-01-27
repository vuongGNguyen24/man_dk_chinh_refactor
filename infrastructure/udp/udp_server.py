import threading
from typing import Callable
from .socket_manager import UDPSocketManager


class UDPServer:
    """
    Infrastructure-level UDP receiver loop
    """

    def __init__(
        self,
        socket_manager: UDPSocketManager,
        on_message: Callable[[bytes, tuple], None],
        buffer_size: int = 4096,
    ):
        self._socket_manager = socket_manager
        self._on_message = on_message
        self._buffer_size = buffer_size
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self):
        if self._running:
            return

        self._running = True
        sock = self._socket_manager.open()

        def _loop():
            while self._running:
                data, addr = sock.recvfrom(self._buffer_size)
                self._on_message(data, addr)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
