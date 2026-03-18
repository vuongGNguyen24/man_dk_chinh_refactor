import serial.rs485
from .base import BaseSerialTransport

class RS485Transport(BaseSerialTransport):
    """
    RS485: half-duplex, multi-drop
    """

    def _configure_transport(self):
        if not self._serial:
            return

        self._serial.rs485_mode = serial.rs485.RS485Settings(
            rts_level_for_tx=True,
            rts_level_for_rx=False,
            delay_before_tx=0.0,
            delay_before_rx=0.0,
        )

    def _before_write(self):
        # pyserial tự control RTS nếu rs485_mode bật
        pass

    def _after_write(self):
        pass
