import socket
import threading
from typing import Optional


class UDPSocketManager:
    """
    Infrastructure component:
    - Quản lý UDP socket
    - Không phụ thuộc UI, domain, application
    """

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port
        self._socket: Optional[socket.socket] = None
        self._lock = threading.Lock()

    def open(self) -> socket.socket:
        if self._socket is None:
            with self._lock:
                if self._socket is None:
                    self._socket = socket.socket(
                        socket.AF_INET, socket.SOCK_DGRAM
                    )
                    self._socket.bind((self._host, self._port))
        return self._socket

    def get_socket(self) -> socket.socket:
        if self._socket is None:
            raise RuntimeError("UDP socket chưa được open()")
        return self._socket

    def close(self) -> None:
        with self._lock:
            if self._socket:
                self._socket.close()
                self._socket = None
