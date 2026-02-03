from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class LogEvent:
    timestamp: datetime
    level: str   # INFO | WARNING | ERROR | SUCCESS
    message: str
