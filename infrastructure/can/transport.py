from abc import ABC, abstractmethod
from typing import Optional

class CANTransport(ABC):
    @abstractmethod
    def open(self) -> None: ...

    @abstractmethod
    def close(self) -> None: ...

    @abstractmethod
    def send(self, arbitration_id: int, data: bytes) -> None: ...

    @abstractmethod
    def receive(self, timeout: float = 0.0):
        """Non-blocking / timeout-based receive"""
