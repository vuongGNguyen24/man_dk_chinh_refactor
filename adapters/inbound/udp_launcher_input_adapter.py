import json
import queue
from typing import List, Tuple

from domain.ports.launcher_input_port import LauncherInputPort
from domain.value_objects import BulletStatus
from infrastructure.udp import UDPServer
from infrastructure.udp import UDPSocketManager


class UDPLauncherInputAdapter(LauncherInputPort):
    """
    Inbound Adapter:
    UDP → Domain Input Port
    """

    def __init__(self, socket_manager: UDPSocketManager):
        self._queue = queue.Queue()
        self._server = UDPServer(
            socket_manager=socket_manager,
            on_message=self._on_message,
        )
        self._server.start()

    # ===== UDP callback =====
    def _on_message(self, data: bytes, addr):
        try:
            message = json.loads(data.decode("utf-8"))
            self._queue.put(message)
        except Exception:
            pass  # log ở infra nếu cần

    # ===== Port methods =====
    def on_angle_feedback(self) -> Tuple[int, float, float]:
        msg = self._wait_for("angle_feedback")
        return (
            msg["launcher_id"],
            float(msg["elevation"]),
            float(msg["azimuth"]),
        )

    def on_azimuth_feedback(self):
        msg = self._wait_for("azimuth_feedback")
        return msg["launcher_id"], float(msg["azimuth"])

    def on_distance_feedback(self) -> float:
        msg = self._wait_for("qdt_feedback")
        return float(msg["distance"])

    def on_ammo_status(self) -> Tuple[int, List[BulletStatus]]:
        msg = self._wait_for("ammo_status")
        bullets = [
            BulletStatus[b] for b in msg["bullets"]
        ]
        return msg["launcher_id"], bullets

    # ===== helper =====
    def _wait_for(self, msg_type: str) -> dict:
        while True:
            msg = self._queue.get()
            if msg.get("type") == msg_type:
                return msg

