from datetime import datetime

from ..dto import LogEvent


class LoggingApplicationService:
    def __init__(self, sink):
        self.sink = sink

    def info(self, msg: str):
        self._emit("INFO", msg)

    def error(self, msg: str):
        self._emit("ERROR", msg)

    def _emit(self, level, msg):
        
        self.sink(LogEvent(datetime.now(), level, msg))
