import struct
import can
import threading
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple, Callable, Any, Literal

from domain.value_objects import BulletStatus
from application.ports.launcher_input_port import LauncherInputPort
from application.dto.angle.packet import AnglePacket
from application.dto import HardwareEventId, LauncherBulletStatus
from infrastructure.can.can_server import CANServer


RESET_COMMAND_TIME = 4
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
        self._last_command_time = {}
        self._lock = threading.Lock()
    def subscribe(self, callback: Callable[[Dict[str, bool]], None]):
        self._subscribers.append(callback)
        
    def on_message(self, msg: can.Message):
        try:
            handler = self.handler_mapping[msg.arbitration_id]
            application_id = self._to_application_id_mapping[msg.arbitration_id]
            
            converted_data = handler(msg)
            
            for callback in self._subscribers:
                callback(application_id, converted_data)

            self._last_command_time[msg.arbitration_id] = time.time()
        except KeyError:
            print(f"No handler for {msg.arbitration_id}")
            return
        
    def on_current_angle_feedback(self, msg: can.Message) -> AnglePacket:
        data = msg.data
        if len(data) == 8:
            elev_raw = (data[1] << 8) | data[2]
            dir_raw  = (data[3] << 8) | data[4]
            elevation = round(elev_raw * 0.1, 1)
            if dir_raw >= 0x8000:
                dir_raw = dir_raw - 0x10000
            direction = round(dir_raw * 0.1, 1)
            return AnglePacket(direction, elevation)
        else:
            print("Invalid angle feedback")
            return
        
    def on_distance_feedback(self, msg: can.Message) -> float:
        data = msg.data
        if len(data) == 4:
            return round(struct.unpack("<f", data)[0], 2)
        else:
            print("Invalid distance feedback")
            return
    
    def on_azimuth_feedback(self, msg: can.Message) -> float:
        data = msg.data
        if len(data) != 4:
            print("Invalid azimuth feedback")
            return

        return round(struct.unpack("<f", bytes(data))[0], 2)    
    def on_ammo_status(self, msg: can.Message) -> LauncherBulletStatus:
        def unpack_bits(n: int, width: int) -> List[bool]:
            return [bool((n>>i) & 1) for i in range(0, width)]
        data = msg.data
        # print("handle amno status")
        # print(data)
        
        flag1 = unpack_bits(data[2], 8)
        flag2 = unpack_bits(data[3], 8)
        flag3 = unpack_bits(data[4], 2)
        return LauncherBulletStatus(flag1 + flag2 + flag3, 
                unpack_bits(data[5], 8) + unpack_bits(data[6], 8) + unpack_bits(data[7], 2))
    
    def disable_launcher(self, launcher_id: Literal['left', 'right']):
        application_id = HardwareEventId.DISABLE_LEFT if launcher_id == 'left' else HardwareEventId.DISABLE_RIGHT
        for callback in self._subscribers:
            callback(application_id, None)
    
    def start(self):
        
        def _loop():
            PACKET_LENGTH = {
            self.CAN_ARBITRATION_ID.ANGLE_CANNON_LEFT: 8,
            self.CAN_ARBITRATION_ID.ANGLE_CANNON_RIGHT: 8,
            self.CAN_ARBITRATION_ID.AMMO_STATUS_LEFT: 8,
            self.CAN_ARBITRATION_ID.AMMO_STATUS_RIGHT: 8}
            
            def in_amno_can_id(can_id: int):
                return can_id == self.CAN_ARBITRATION_ID.AMMO_STATUS_LEFT or can_id == self.CAN_ARBITRATION_ID.AMMO_STATUS_RIGHT
            
            while True:
                now = time.time()
                need_delete_id: List[int] = []
                for can_id, last_command_time in self._last_command_time.items():
                    if can_id not in PACKET_LENGTH:
                        continue
                    if now - last_command_time < RESET_COMMAND_TIME:
                        continue
                    print("reset id", hex(can_id))
                    if in_amno_can_id(can_id):
                        launcher_id = 'left' if can_id == self.CAN_ARBITRATION_ID.AMMO_STATUS_LEFT else 'right'
                        self.disable_launcher(launcher_id)
                    else:
                        self.on_message(can.Message(arbitration_id=can_id, 
                                                data=bytes([0] * PACKET_LENGTH[can_id])))
                    need_delete_id.append(can_id)
                time.sleep(0.5)

                for can_id in need_delete_id:
                    self._last_command_time.pop(can_id)
        
        self._thread = threading.Thread(target=_loop, daemon=True)
        self._thread.start()