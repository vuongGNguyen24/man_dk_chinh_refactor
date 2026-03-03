import struct
import can
from dataclasses import dataclass
from typing import Dict, List, Tuple, Callable, Any

from domain.value_objects import BulletStatus
from application.ports.launcher_input_port import LauncherInputPort
from application.dto.angle.packet import AnglePacket
from application.dto import HardwareEventId
from infrastructure.can.can_server import CANServer
@dataclass(frozen=True)
class CANArbitrationID:
    # --- Khoảng cách và Hướng từ Quang điện tử ---
    DISTANCE: int = 0x100          # ID nhận khoảng cách (4 bytes, float)
    AZIMUTH: int = 0x102         # ID nhận hướng (4 bytes, float)

    # --- Góc hiện tại của Pháo (từ cảm biến encoder) ---
    ANGLE_CANNON_LEFT: int = 0x00F       # ID nhận góc pháo trái (8 bytes: angle + direction)
    ANGLE_CANNON_RIGHT: int = 0x00E     # ID nhận góc pháo phải (8 bytes: angle + direction)
    ERROR: int = 0x004
    # --- Trạng thái đạn ---
    AMMO_STATUS_LEFT: int = 0x98   # ID nhận trạng thái ống phóng giàn trái
    AMMO_STATUS_RIGHT: int = 0x99  # ID nhận trạng thái ống phóng giàn phải


class CANLauncherInputAdapter(LauncherInputPort):
    
    
    def __init__(self, can_server: CANServer):
        self._can_server = can_server
        self.CAN_ARBITRATION_ID = CANArbitrationID()
        self._subscribers: List[Callable[[int, Any], None]] = []
        self.handler_mapping = {
            self.CAN_ARBITRATION_ID.DISTANCE: self.on_distance_feedback,
            self.CAN_ARBITRATION_ID.AZIMUTH: self.on_azimuth_feedback,
            self.CAN_ARBITRATION_ID.ANGLE_CANNON_LEFT: self.on_current_angle_feedback,
            self.CAN_ARBITRATION_ID.ANGLE_CANNON_RIGHT: self.on_current_angle_feedback,
            self.CAN_ARBITRATION_ID.AMMO_STATUS_LEFT: self.on_ammo_status,
            self.CAN_ARBITRATION_ID.AMMO_STATUS_RIGHT: self.on_ammo_status,
        }
        self._to_application_id_mapping = {
            self.CAN_ARBITRATION_ID.AMMO_STATUS_LEFT: HardwareEventId.AMMO_STATUS_LEFT,
            self.CAN_ARBITRATION_ID.AMMO_STATUS_RIGHT: HardwareEventId.AMMO_STATUS_RIGHT,
            self.CAN_ARBITRATION_ID.ANGLE_CANNON_LEFT: HardwareEventId.ANGLE_LEFT,
            self.CAN_ARBITRATION_ID.ANGLE_CANNON_RIGHT: HardwareEventId.ANGLE_RIGHT,
            self.CAN_ARBITRATION_ID.DISTANCE: HardwareEventId.DISTANCE, 
            self.CAN_ARBITRATION_ID.AZIMUTH: HardwareEventId.AZIMUTH,
        }
    def subcribe(self, callback: Callable[[Dict[str, bool]], None]):
        self._subscribers.append(callback)
        
    def on_message(self, msg: can.Message):
        try:
            handler = self.handler_mapping[msg.arbitration_id]
            application_id = self._to_application_id_mapping[msg.arbitration_id]
            
            converted_data = handler(msg)
            for callback in self._subscribers:
                callback(application_id, converted_data)
        except KeyError:
            print(f"No handler for {msg.arbitration_id}")
            return
        
    def on_current_angle_feedback(self, msg: can.Message) -> AnglePacket:
        data = msg.data
        if len(data) == 6:
            elev_raw = (data[1] << 8) | data[2]
            dir_raw  = (data[3] << 8) | data[4]
            angle = elev_raw * 0.1
            if dir_raw >= 0x8000:
                dir_raw = dir_raw - 0x10000
            direction = dir_raw * 0.01
            return AnglePacket(angle, direction)
        else:
            raise ValueError("Invalid angle feedback")
        
    def on_distance_feedback(self, msg: can.Message) -> float:
        data = msg.data
        if len(data) == 4:
            return struct.unpack("<f", data)[0]
        else:
            raise ValueError("Invalid distance feedback")
        
    def on_ammo_status(self, msg: can.Message) -> List[bool]:
        def unpack_bits(n: int, width: int) -> List[bool]:
            return [bool((n>>i) & 1) for i in range(0, width)]
        data = msg.data
        print(data)
        
        flag1 = unpack_bits(data[2], 8)
        flag2 = unpack_bits(data[3], 8)
        flag3 = unpack_bits(data[4], 2)
        return flag1 + flag2 + flag3