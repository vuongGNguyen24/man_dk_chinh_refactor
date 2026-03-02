from typing import Dict, Optional, Callable, List
import struct
import time
from infrastructure.serial import SerialConfig, RS485Transport
from application.dto import ElectricalPointStatus
from application.ports.electrical_circuit import ElectricalPointInputPort


class RS485ElectricalPointInputAdapter(ElectricalPointInputPort):
    def __init__(
        self,
        serial_config: SerialConfig,
        decode_mapping_choice: Dict[int, Dict[int, str]],
    ):
        self.transport = RS485Transport(serial_config)
        self.subscribers: List[Callable[[Dict[str, bool]], None]] = []
        self.decode_mapping_choice: Dict[int, Dict[int, str]] = decode_mapping_choice
        self.valid_ids: List[int] = self.decode_mapping_choice.keys()
        self.running = False
            
    def subscribe(self, callback: Callable[[Dict[str, bool]], None]):
        self.subscribers.append(callback)
    
    def is_valid_packet(self, packet: bytes) -> bool:
        return (
            packet[0] in self.vaild_ids 
            and packet[-2] == 0x21
            and packet[-1] == 0x22
        )
        
    def read_points(self):
        packet = self.transport.read(6)
        
        if not packet:
            return None
        
        if self.is_valid_packet(packet):
            return self._decode_bitmask(packet[1:-2], self.decode_mapping_choice[packet[0]])
        
        return None
        
    
    def _decode_bitmask(
        self, data: bytes, bit_mask_to_point_id: Dict[int, str]
    ) -> Dict[str, bool]:
        """
        Decode payload thành Pxx -> bool
        """
        
        def get_bit(mask, bit_index):
            return (mask >> bit_index) & 1
        
        
        result: Dict[str, bool] = {}
        tmp = struct.unpack(">I", data)
        for bit_index, point_id in bit_mask_to_point_id.items():
            result[point_id] = get_bit(tmp[0], bit_index)
        
        return result
    
            
    def run(self):
        self.running = True
        with self.transport:
            while True:
                snapshot = self.read_points()
                if snapshot and self.subscribers:
                    for func in self.subscribers:
                        func(snapshot)
                time.sleep(0.03)