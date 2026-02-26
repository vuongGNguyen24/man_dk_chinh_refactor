import can
import threading
from typing import Optional


class CANBusManager:
    """
    Infrastructure component:
    - Quản lý CAN bus
    - Không phụ thuộc UI, domain, application
    """

    def __init__(self, channel: str, bitrate: int):
        self._channel = channel
        self._bitrate = bitrate
        self._bus: Optional[can.Bus] = None
        self._lock = threading.Lock()

    def open(self) -> can.Bus:
        if self._bus is None:
            with self._lock:
                if self._bus is None:
                    self._bus = can.Bus(
                        interface="socketcan",
                        channel=self._channel,
                        bitrate=self._bitrate,
                    )
        return self._bus

    def get_bus(self) -> can.Bus:
        if self._bus is None:
            raise RuntimeError("CAN bus chưa được open()")
        return self._bus

    def close(self) -> None:
        with self._lock:
            if self._bus:
                self._bus.shutdown()
                self._bus = None