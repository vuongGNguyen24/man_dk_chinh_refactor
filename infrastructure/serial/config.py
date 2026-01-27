from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class SerialConfig:
    port: str
    baudrate: int = 115200
    bytesize: int = 8
    parity: str = 'N'
    stopbits: int = 1
    timeout: Optional[float] = 0.1
    write_timeout: Optional[float] = 0.1
