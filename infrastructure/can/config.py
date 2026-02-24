from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class CANConfig:
    channel: str = "can0"
    bustype: str = "socketcan"
    bitrate: int = 500000
    
    @staticmethod
    def from_dict(d: dict) -> 'CANConfig':
        return CANConfig(
            channel=d["channel"],
            bustype=d.get("bustype", "socketcan"),
            bitrate=d.get("bitrate", 500000),
        )