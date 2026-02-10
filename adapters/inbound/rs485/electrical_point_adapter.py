from typing import Dict
import struct
from infrastructure.serial import SerialConfig, RS485Transport
from application.dto import ElectricalPointStatus
from application.ports.electrical_circuit import ElectricalPointInputPort


class RS485ElectricalPointInputAdapter(ElectricalPointInputPort):
    def __init__(
        self,
        serial_config: SerialConfig,
    ):
        self.transport = RS485Transport(serial_config)
        self.bit_mask_to_point_id: Dict[int, str] = {}
    def read_points(self):
        packet = self.transport.read(6)
        
        if not packet:
            return None
        
        if packet[0] == 0x01 and packet[-2] == 0x21 and packet[-1] == 0x22:
            return self._decode_bitmask(0, packet[1:-2])
        
        return None
        
    
    def _decode_bitmask(
        self, node_id: int, data: bytes
    ) -> Dict[str, bool]:
        """
        Decode payload thành Pxx -> bool
        """
        
        def get_bit(mask, bit_index):
            return (mask >> bit_index) & 1
        
        
        result: Dict[str, bool] = {}
        tmp = struct.unpack(">I", data)
        for bit_index, point_id in self.bit_mask_to_point_id.items():
            result[point_id] = get_bit(tmp[0], bit_index)
        
        return result