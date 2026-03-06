from typing import Literal
# from dataclasses import dataclass
from datetime import datetime

# @dataclass(frozen=True)
class LogEvent:
    def __init__(self, level: Literal['INFO', 'WARNING', 'ERROR', 'SUCCESS'], message: str):
        self.level = level
        self.message = message
        self.timestamp = datetime.now()
