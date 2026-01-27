from .base import BaseSerialTransport

class RS422Transport(BaseSerialTransport):
    """
    RS422: full-duplex, không cần direction control
    """

    def _configure_transport(self):
        # RS422 không cần cấu hình đặc biệt
        pass
