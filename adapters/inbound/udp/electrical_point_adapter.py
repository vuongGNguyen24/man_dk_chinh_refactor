from typing import Dict, Optional
import struct
import threading

from application.ports.electrical_circuit import ElectricalPointInputPort
from application.dto import ElectricalPointStatus
from infrastructure.udp import UDPServer, UDPSocketManager


class UDPElectricalPointInputAdapter(ElectricalPointInputPort):
    """
    Adapter nhận trạng thái điểm mạch điện qua UDP
    - Packet format GIỐNG RS485
    """

    def __init__(
        self,
        socket_manager: UDPSocketManager,
        buffer_size: int = 4096,
    ):
        self._latest_packet: Optional[bytes] = None
        self._lock = threading.Lock()

        self.bit_mask_to_point_id: Dict[int, str] = {}

        self._server = UDPServer(
            socket_manager=socket_manager,
            on_message=self._on_message,
            buffer_size=buffer_size,
        )
        self._server.start()

    # ---------- UDP callback ----------

    def _on_message(self, data: bytes, addr):
        """
        Được gọi từ thread UDPServer
        """
        with self._lock:
            self._latest_packet = data

    # ---------- Application Port ----------

    def read_points(self):
        """
        Pull-style API giống RS485
        """
        with self._lock:
            packet = self._latest_packet
            self._latest_packet = None

        if not packet:
            return None

        # Protocol giống hệt RS485
        if packet[0] == 0x01 and packet[-2] == 0x21 and packet[-1] == 0x22:
            return self._decode_bitmask(
                node_id=0,
                data=packet[1:-2],
            )

        return None

    # ---------- Shared decode logic ----------

    def _decode_bitmask(
        self,
        node_id: int,
        data: bytes,
    ) -> Dict[str, bool]:
        """
        Decode payload thành:
        {
            "P01": True,
            "P02": False,
            ...
        }
        """

        def get_bit(mask, bit_index):
            return (mask >> bit_index) & 1

        result: Dict[str, bool] = {}
        tmp = struct.unpack(">I", data)

        for bit_index, point_id in self.bit_mask_to_point_id.items():
            result[point_id] = bool(get_bit(tmp[0], bit_index))

        return result
