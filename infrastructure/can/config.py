from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CANConfig:
    channel: str = "can0"
    bustype: str = "socketcan"
    bitrate: int = 500000