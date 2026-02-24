import serial
import threading
from abc import ABC, abstractmethod
from .config import SerialConfig


class BaseSerialTransport(ABC):
    """
    Infrastructure-level serial transport.
    Không biết protocol, không biết domain.
    """

    def __init__(self, config: SerialConfig):
        self._config = config
        self._serial: serial.Serial | None = None
        self._lock = threading.Lock()

    def open(self):
        if self._serial and self._serial.is_open:
            return

        self._serial = serial.Serial(
            port=self._config.port,
            baudrate=self._config.baudrate,
            bytesize=self._config.bytesize,
            parity=self._config.parity,
            stopbits=self._config.stopbits,
            timeout=self._config.timeout,
            write_timeout=self._config.write_timeout,
        )

        self._configure_transport()

    def close(self):
        if self._serial and self._serial.is_open:
            self._serial.close()

    def write(self, data: bytes):
        if not self._serial:
            raise RuntimeError("Serial port not opened")

        with self._lock:
            self._before_write()
            self._serial.write(data)
            self._serial.flush()
            self._after_write()

    def read(self, size: int = 1) -> bytes:
        if not self._serial:
            raise RuntimeError("Serial port not opened")
        return self._serial.read(size)

    def read_until(self, terminator: bytes = b'\n') -> bytes:
        if not self._serial:
            raise RuntimeError("Serial port not opened")
        return self._serial.read_until(terminator)

    @abstractmethod
    def _configure_transport(self):
        """Hook cho RS485 / RS422"""

    def _before_write(self):
        pass

    def _after_write(self):
        pass

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()