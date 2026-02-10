from typing import Dict
import can
import struct

from application.ports.electrical_circuit import ElectricalPointInputPort
from infrastructure.can.bus_manager import can_bus_manager
from infrastructure.can.can_node_registry import CanNodeRegistry
from application.dto import ElectricalPointStatus

class CANElectricalPointInputAdapter(ElectricalPointInputPort):
    """
    Adapter đọc trạng thái điện từ CAN
    và expose dưới dạng Dict[str, bool] cho application.
    """

    def __init__(
        self,
        registry: CanNodeRegistry,
        bus_manager=can_bus_manager,
        timeout: float = 0.05,
    ):
        self._registry = registry
        self._bus_manager = bus_manager
        self._timeout = timeout

        # cache trạng thái cuối cùng
        self._state: Dict[str, bool] = {}

    def read_points(self) -> Dict[str, bool]:
        """
        Đọc toàn bộ frame CAN đang có trong buffer,
        cập nhật snapshot trạng thái điểm điện.
        """
        bus = self._bus_manager.get_bus()

        while True:
            msg = bus.recv(timeout=self._timeout)
            if msg is None:
                break

            self._handle_message(msg)

        return dict(self._state)

    # -------------------------
    # internal
    # -------------------------

    def _handle_message(self, msg: can.Message) -> None:
        """
        Parse CAN frame -> update point state
        """
        node_id = self._resolve_node_id(msg.arbitration_id)
        if node_id is None:
            return

        points = self._decode_bitmask(node_id, msg.data)
        self._state.update(points)

    def _resolve_node_id(self, arbitration_id: int) -> int | None:
        """
        Ví dụ mapping:
            CAN ID = 0x300 + node_id
        """
        base = 0x300
        if arbitration_id < base:
            return None
        return arbitration_id - base

    def _decode_bitmask(
        self, node_id: int, data: bytes
    ) -> Dict[str, bool]:
        """
        Decode payload thành Pxx -> bool
        """
        result: Dict[str, bool] = {}

        for byte_index, byte in enumerate(data):
            for bit in range(8):
                point_index = byte_index * 8 + bit + 1
                point_id = f"P{point_index:02d}"

                powered = bool(byte & (1 << bit))
                result[point_id] = powered

        return result

