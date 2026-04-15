from typing import Dict, Optional, Callable, List, Tuple
import struct
import time
import threading
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
        self.valid_ids: List[tuple[int, int]] = self.decode_mapping_choice.keys()
        self.running = False
            
    def subscribe(self, callback: Callable[[Dict[str, bool]], None]):
        self.subscribers.append(callback)
    
    def is_valid_packet(self, packet: bytes) -> bool:
        return (
            len(packet) == 8 
            and self._get_header_ids(packet) in self.valid_ids
            and packet[-2] == 0x21
            and packet[-1] == 0x22
        )
    
    def _get_header_ids(self, packet: bytes) -> Tuple[int, int]:
        return (packet[0], packet[1])

    def read_points(self):
        packet = self.transport.read(8)
        
        if not packet:
            return None
        
        if self.is_valid_packet(packet):
            return self._decode_bitmask(packet[2:6], self.decode_mapping_choice[self._get_header_ids(packet)])
        
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
        tmp = struct.unpack("<I", data)
        for bit_index, point_id in bit_mask_to_point_id.items():
            result[point_id] = get_bit(tmp[0], bit_index)
        
        return result
    
            
    def start(self):
        if self.running:
            return
        self.running = True
        self.transport.open()

        def _loop():
            last_command_time = time.time()
            SEND_INTERVAL = 1.5
            sent_left_laucher = 1
            sent_data = [0x6D, 0, 1, 0xAE]
            while True:
                now = time.time()
                if now - last_command_time > SEND_INTERVAL:
                    sent_data[1] = (sent_left_laucher ^ 1)
                    # print(sent_data)
                    self.transport.write(bytes(sent_data))
                    sent_left_laucher ^= 1
                    last_command_time = now

                snapshot = self.read_points()
                # print(snapshot)
                if snapshot and self.subscribers:
                    for func in self.subscribers:
                        func(snapshot)
                time.sleep(0.03)

        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()