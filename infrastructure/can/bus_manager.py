import threading
import can
from infrastructure.can.config import CANConfig

class CANBusManager:
    _instance = None
    _lock = threading.Lock()
    _bus = None

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def open_bus(self, config: CANConfig):
        if self._bus is None:
            with self._lock:
                if self._bus is None:
                    self._bus = can.interface.Bus(
                        channel=config.channel,
                        bustype=config.bustype,
                        bitrate=config.bitrate,
                    )

    def get_bus(self) -> can.Bus:
        if self._bus is None:
            self.open_bus()
        return self._bus

    def close_bus(self):
        if self._bus is not None:
            with self._lock:
                if self._bus is not None:
                    self._bus.shutdown()
                    self._bus = None


can_bus_manager = CANBusManager()
