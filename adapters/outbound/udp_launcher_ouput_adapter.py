import json
import socket

from domain.ports.launcher_output_port import LauncherCommandPort
from infrastructure.udp import UDPSocketManager
 
 
class UDPLauncherOutputAdapter(LauncherCommandPort):
    """
    Outbound Adapter:
    Domain Command → UDP
    """

    def __init__(self, socket_manager: UDPSocketManager, target_addr: tuple[str, int]):
        self._socket = socket_manager.open()
        self._target = target_addr

    def select_bullets(self, launcher_id: str, bullets: list[int]):
        self._send({
            "type": "select_bullets",
            "launcher_id": launcher_id,
            "bullets": bullets,
        })

    def set_target_azimuth(self, launcher_id: str, angle_deg: float):
        self._send({
            "type": "set_azimuth",
            "launcher_id": launcher_id,
            "azimuth": angle_deg,
        })

    def set_target_elevation(self, launcher_id: str, angle_deg: float):
        self._send({
            "type": "set_elevation",
            "launcher_id": launcher_id,
            "elevation": angle_deg,
        })

    def _send(self, payload: dict):
        data = json.dumps(payload).encode("utf-8")
        self._socket.sendto(data, self._target)
