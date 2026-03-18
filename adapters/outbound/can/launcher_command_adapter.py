from typing import Set, Union, Literal
import struct
from dataclasses import dataclass
from application.ports.launcher_output_port import LauncherCommandPort
from application.dto.angle.packet import AnglePacket
from infrastructure.can.can_server import CANServer


@dataclass(frozen=True)
class CANArbitrationID:
    LAUNCH_COMMAND: int = 0x29
    ANGLE_LEFT: int = 0x05C
    ANGLE_RIGHT: int = 0x01B


@dataclass(frozen=True)
class CANCommandID:
    END: int = 0x11
    SELECT_BULLETS_HEADER: int = 0x29
    SELECT_BULLETS_LEFT: int = 0x30
    SELECT_BULLETS_RIGHT: int = 0x31
    ANGLE_INPUT_HEADER: int = 0x11
    MARKER: int = 0x99


class CANLauncherCommandAdapter(LauncherCommandPort):
    """
    Outbound Adapter:
    - Implement LauncherCommandPort
    - Encode application DTO -> CAN frame
    - Không để application biết gì về CAN
    """
    
    
    def __init__(self, can_server: CANServer):
        self._can_server = can_server
        self.CAN_COMMAND_ID = CANCommandID()
        self.CAN_ARBITRATION_ID = CANArbitrationID()

    def select_bullets(self, launcher_id: Literal["left", "right"], bullets: Set[int]) -> None:
        """Gửi tín hiệu chọn đạn đến phần cứng

        Args:
            launcher_id (Literal[&quot;left&quot;, &quot;right&quot;]): giàn trái hay giàn phải
            bullets (Set[int]): danh sách ống phóng được chọn, tính vị trí từ 1 đến 18
        """
        arbitration_id = self.CAN_ARBITRATION_ID.LAUNCH_COMMAND

        payload = self._encode_select_bullets(launcher_id, bullets)

        try:
            self._can_server.send(
                arbitration_id=arbitration_id,
                data=payload,
                is_extended_id=False,
            )
            print(f"CAN send select_bullets success: arbitration_id={hex(arbitration_id)}, payload={payload.hex()}")
        except Exception as e:
            print(f"CAN send select_bullets error: {e}")

    def send_target_angle(
        self,
        launcher_id: Literal["left", "right"],
        angle_input_deg: AnglePacket,
    ) -> None:
        """
        Encode góc phương vị & góc tầm thành CAN payload
        """
        arbitration_id = self.CAN_ARBITRATION_ID.ANGLE_LEFT if launcher_id == "left" else self.CAN_ARBITRATION_ID.ANGLE_RIGHT

        payload = self._encode_angle_input(angle_input_deg)

        try:
            self._can_server.send(
                arbitration_id=arbitration_id,
                data=payload,
                is_extended_id=False,
            )
            print(f"CAN send send_target_angle success: arbitration_id={hex(arbitration_id)}, payload={payload.hex()}")
        except Exception as e:
            print(f"CAN send send_target_angle error: {e}")

    def _encode_select_bullets(self, launcher_id: Literal["left", "right"], bullets: Set[int]) -> bytes:
        """Encode theo dạng 7 bytes:
                - 0x29: Bắt đầu gói tin
                 
                - 0x31 hoặc 0x32:	"Chọn đạn cho: giàn trái -> 0x31, giàn phải -> 0x32"
                
                - 24 bit chọn đạn cho các ống phóng với: 1: chọn đạn, 0: không chọn đạn	
        
                - 0x99: Đánh dấu
                
                - 0x11: Kết thúc gói tin

        Args:
            launcher_id (Literal[&quot;left&quot;, &quot;right&quot;]): chọn đạn cho giàn trái hay giàn phải
            bullets (Set[int]): danh sách đạn được chọn

        Returns:
            bytes: byte array chứa danh sách đạn được chọn
        """
        mask = 0
        for bullet in bullets:
            mask |= 1 << (bullet - 1)
        
        return bytes([
            self.CAN_COMMAND_ID.SELECT_BULLETS_HEADER,
            self.CAN_COMMAND_ID.SELECT_BULLETS_LEFT if launcher_id == "left" else self.CAN_COMMAND_ID.SELECT_BULLETS_RIGHT,
            mask & 0xFF,
            (mask >> 8) & 0xFF,
            (mask >> 16) & 0xFF,
            self.CAN_COMMAND_ID.MARKER,
            self.CAN_COMMAND_ID.END,
        ])
            

    def _encode_angle_input(self, packet: AnglePacket) -> bytes:
        """
        Tạm encode:
        - 2 float32: azimuth, elevation
        Tổng 6 bytes
        """

        #using 16 bit integer of 10 times of angle
        azimuth_bytes = struct.pack("<h", int(packet.azimuth * 10))
        elevation_bytes = struct.pack("<h", int(packet.elevation * 10))
        data_launch = [
            self.CAN_COMMAND_ID.ANGLE_INPUT_HEADER,
            *azimuth_bytes,
            *elevation_bytes,
            self.CAN_COMMAND_ID.END,
        ]
        return bytes(data_launch)