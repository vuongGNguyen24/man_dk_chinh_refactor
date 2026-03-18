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
    
    @staticmethod
    def from_dict(d: dict) -> 'SerialConfig':
        return SerialConfig(
            port=d["port"],
            baudrate=d.get("baudrate", 115200),
            bytesize=d.get("bytesize", 8),
            parity=d.get("parity", 'N'),
            stopbits=d.get("stopbits", 1),
            timeout=d.get("timeout", 0.1),
            write_timeout=d.get("write_timeout", 0.1),
        )
        
if __name__ == "__main__":
    d = {'port': '/dev/ttyUSB0', 'baudrate': 9600, 'bytesize': 8, 'parity': 'N', 'stopbits': 1, 'timeout': 0.05, 'write_timeout': 0.05}
    config = SerialConfig.from_dict(d)
    print(config)
