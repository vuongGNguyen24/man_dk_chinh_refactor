import json
import struct
from typing import Set, Literal
from dataclasses import dataclass

from application.ports.launcher_output_port import LauncherCommandPort
from application.dto.angle.packet import AnglePacket
from infrastructure.udp import UDPServer


@dataclass(frozen=True)
class LegacyArbitrationID:
    LAUNCH_COMMAND: int = 0x29
    ANGLE_LEFT: int = 0x05C
    ANGLE_RIGHT: int = 0x01B


@dataclass(frozen=True)
class LegacyCommandID:
    END: int = 0x11
    SELECT_BULLETS_HEADER: int = 0x29
    SELECT_BULLETS_LEFT: int = 0x30
    SELECT_BULLETS_RIGHT: int = 0x31
    ANGLE_INPUT_HEADER: int = 0x11
    MARKER: int = 0x99


class UDPLauncherCommandAdapter(LauncherCommandPort):
    """
    Outbound Adapter qua UDP
    - Encode giống CAN
    - Wrap thành JSON { arbitration_id, data }
    """

    def __init__(
        self,
        udp_server: UDPServer,
        target_ip: str,
        target_port: int,
    ):
        self._udp_server = udp_server
        self._target_ip = target_ip
        self._target_port = target_port

        self.LEGACY_COMMAND_ID = LegacyCommandID()
        self.LEGACY_ARBITRATION_ID = LegacyArbitrationID()

    # --------------------------------------------------

    def select_bullets(
        self,
        launcher_id: Literal["left", "right"],
        bullets: Set[int],
    ) -> None:

        arbitration_id = self.LEGACY_ARBITRATION_ID.LAUNCH_COMMAND
        payload_bytes = self._encode_select_bullets(launcher_id, bullets)

        self._send_udp(arbitration_id, payload_bytes)

    # --------------------------------------------------

    def send_target_angle(
        self,
        launcher_id: Literal["left", "right"],
        angle_input_deg: AnglePacket,
    ) -> None:

        arbitration_id = (
            self.LEGACY_ARBITRATION_ID.ANGLE_LEFT
            if launcher_id == "left"
            else self.LEGACY_ARBITRATION_ID.ANGLE_RIGHT
        )

        payload_bytes = self._encode_angle_input(angle_input_deg)

        self._send_udp(arbitration_id, payload_bytes)

    # --------------------------------------------------

    def _send_udp(self, arbitration_id: int, payload: bytes) -> None:

        packet = {
            "arbitration_id": arbitration_id,
            "data": list(payload),  # convert bytes -> list[int] để JSON serializable
        }

        raw = json.dumps(packet).encode("utf-8")

        try:
            self._udp_server.send(
                data=raw,
                ip_address=self._target_ip,
                port=self._target_port,
            )
            print(f"UDP send success: arbitration_id={hex(arbitration_id)}, data={raw.decode('utf-8')}")
        except Exception as e:
            print(f"UDP send error: {e}")

    # --------------------------------------------------
    # Encode logic (giữ nguyên từ CAN adapter)
    # --------------------------------------------------

    def _encode_select_bullets(
        self,
        launcher_id: Literal["left", "right"],
        bullets: Set[int],
    ) -> bytes:

        mask = 0
        for bullet in bullets:
            mask |= 1 << bullet

        return bytes([
            self.LEGACY_COMMAND_ID.SELECT_BULLETS_HEADER,
            self.LEGACY_COMMAND_ID.SELECT_BULLETS_LEFT
            if launcher_id == "left"
            else self.LEGACY_COMMAND_ID.SELECT_BULLETS_RIGHT,
            mask & 0xFF,
            (mask >> 8) & 0xFF,
            (mask >> 16) & 0xFF,
            self.LEGACY_COMMAND_ID.MARKER,
            self.LEGACY_COMMAND_ID.END,
        ])

    def _encode_angle_input(self, packet: AnglePacket) -> bytes:

        azimuth_bytes = struct.pack("<h", int(packet.azimuth * 10))
        elevation_bytes = struct.pack("<h", int(packet.elevation * 10))

        return bytes([
            self.LEGACY_COMMAND_ID.ANGLE_INPUT_HEADER,
            *azimuth_bytes,
            *elevation_bytes,
            self.LEGACY_COMMAND_ID.END,
        ])