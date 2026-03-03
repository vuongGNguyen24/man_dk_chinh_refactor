import json
import struct
from dataclasses import dataclass
from typing import Callable, List, Any, Dict

from application.ports.launcher_input_port import LauncherInputPort
from application.dto.angle.packet import AnglePacket
from application.dto import HardwareEventId
from domain.value_objects import BulletStatus
from infrastructure.udp import UDPServer


@dataclass(frozen=True)
class LegacyArbitrationID:
    DISTANCE: int = 0x100
    AZIMUTH: int = 0x102
    ANGLE_CANNON_LEFT: int = 0x00F
    ANGLE_CANNON_RIGHT: int = 0x00E
    AMMO_STATUS_LEFT: int = 0x98
    AMMO_STATUS_RIGHT: int = 0x99


class UDPLauncherInputAdapter(LauncherInputPort):

    def __init__(self, udp_server: UDPServer):
        self._subscribers: List[Callable[[HardwareEventId, Any], None]] = []
        self.LEGACY_ID = LegacyArbitrationID()

        self._handler_mapping = {
            self.LEGACY_ID.DISTANCE: self._on_distance_feedback,
            self.LEGACY_ID.AZIMUTH: self._on_azimuth_feedback,
            self.LEGACY_ID.ANGLE_CANNON_LEFT: self._on_current_angle_feedback,
            self.LEGACY_ID.ANGLE_CANNON_RIGHT: self._on_current_angle_feedback,
            self.LEGACY_ID.AMMO_STATUS_LEFT: self._on_ammo_status,
            self.LEGACY_ID.AMMO_STATUS_RIGHT: self._on_ammo_status,
        }

        self._to_application_id_mapping = {
            self.LEGACY_ID.AMMO_STATUS_LEFT: HardwareEventId.AMMO_STATUS_LEFT,
            self.LEGACY_ID.AMMO_STATUS_RIGHT: HardwareEventId.AMMO_STATUS_RIGHT,
            self.LEGACY_ID.ANGLE_CANNON_LEFT: HardwareEventId.ANGLE_LEFT,
            self.LEGACY_ID.ANGLE_CANNON_RIGHT: HardwareEventId.ANGLE_RIGHT,
            self.LEGACY_ID.DISTANCE: HardwareEventId.DISTANCE,
            self.LEGACY_ID.AZIMUTH: HardwareEventId.AZIMUTH,
        }

        udp_server.subscribe(self.on_message)

    # -----------------------------------------------------

    def subscribe(self, callback: Callable[[HardwareEventId, Any], None]):
        self._subscribers.append(callback)

    # -----------------------------------------------------

    def on_message(self, raw_data: bytes, addr: str):

        try:
            payload = json.loads(raw_data.decode("utf-8"))
        except Exception:
            return

        arbitration_id = payload.get("arbitration_id")
        data = payload.get("data")

        if arbitration_id not in self._handler_mapping:
            return

        handler = self._handler_mapping[arbitration_id]
        application_id = self._to_application_id_mapping[arbitration_id]

        try:
            converted_data = handler(data)
        except Exception:
            return

        for cb in self._subscribers:
            cb(application_id, converted_data)

    # -----------------------------------------------------
    # Decode logic (giống CAN adapter)
    # -----------------------------------------------------

    def _on_current_angle_feedback(self, data: List[int]) -> AnglePacket:

        if len(data) != 6:
            raise ValueError("Invalid angle feedback")

        elev_raw = (data[1] << 8) | data[2]
        dir_raw = (data[3] << 8) | data[4]

        angle = elev_raw * 0.1

        if dir_raw >= 0x8000:
            dir_raw -= 0x10000

        direction = dir_raw * 0.01

        return AnglePacket(angle, direction)

    def _on_distance_feedback(self, data: List[int]) -> float:

        if len(data) != 4:
            raise ValueError("Invalid distance feedback")

        return struct.unpack("<f", bytes(data))[0]

    def _on_azimuth_feedback(self, data: List[int]) -> float:

        if len(data) != 4:
            raise ValueError("Invalid azimuth feedback")

        return struct.unpack("<f", bytes(data))[0]

    def _on_ammo_status(self, data: List[int]) -> List[bool]:

        if len(data) < 5:
            raise ValueError("Invalid ammo status")

        def unpack_bits(n: int, width: int) -> List[bool]:
            return [bool((n >> i) & 1) for i in range(width)]

        flag1 = unpack_bits(data[2], 8)
        flag2 = unpack_bits(data[3], 8)
        flag3 = unpack_bits(data[4], 2)

        return flag1 + flag2 + flag3