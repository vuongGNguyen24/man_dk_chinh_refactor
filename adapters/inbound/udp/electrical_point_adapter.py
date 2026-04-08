from typing import Dict, Callable, List, Tuple
import struct
import threading

from application.ports.electrical_circuit import ElectricalPointInputPort
from infrastructure.udp import UDPServer

class UDPElectricalPointInputAdapter(ElectricalPointInputPort):
    """
    Push-style adapter
    """

    def __init__(self, decode_mapping_choice: Dict[Tuple[str, int], Dict[int, str]]):

        self._subscribers: List[Callable[[Dict[str, bool]], None]] = []
        self._lock = threading.Lock()
        self.decode_mapping_choice: Dict[Tuple[str, int], Dict[int, str]] = decode_mapping_choice
        self.valid_ids = [item[-1] for item in self.decode_mapping_choice.keys()]

    def subscribe(self, callback: Callable[[Dict[str, bool]], None]):
        self._subscribers.append(callback)

    # ---------- UDP callback ----------

    def on_message(self, data: bytes, addr: str):

        if not self._is_valid_packet(data):
            return
        snapshot = self._decode_bitmask(
            data=data[2:-2],
            bit_mask_to_point_id=self.decode_mapping_choice[(addr, data[0])],
        )

        if not snapshot:
            return

        # push sang service
        for cb in self._subscribers:
            cb(snapshot)

    def _is_valid_packet(self, packet: bytes) -> bool:
        return (
            len(packet) == 8
            and packet[0] in self.vaild_ids 
            and packet[-2] == 0x21
            and packet[-1] == 0x22
        )

    def _decode_bitmask(self, data: bytes, bit_mask_to_point_id: Dict[int, str]) -> Dict[str, bool]:

        def get_bit(mask, bit_index):
            return (mask >> bit_index) & 1

        result: Dict[str, bool] = {}
        tmp = struct.unpack(">I", data)

        for bit_index, point_id in bit_mask_to_point_id.items():
            result[point_id] = bool(get_bit(tmp[0], bit_index))

        return result
    
