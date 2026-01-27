import json
import queue
from typing import Dict, Tuple

from domain.ports.node_input_port import NodeInputPort
from domain.value_objects.parameter import Parameter
from infrastructure.udp import UDPServer
from infrastructure.udp import UDPSocketManager


class UDPNodeInputAdapter(NodeInputPort):
    """
    Inbound Adapter:
    UDP → NodeInputPort
    """

    def __init__(self, socket_manager: UDPSocketManager):
        self._queue = queue.Queue()

        self._server = UDPServer(
            socket_manager=socket_manager,
            on_message=self._on_message,
        )
        self._server.start()

    # ================= UDP callback =================
    def _on_message(self, data: bytes, addr):
        try:
            msg = json.loads(data.decode("utf-8"))
            self._queue.put(msg)
        except Exception:
            pass  # log ở infra nếu cần

    # ================= Port methods =================
    def on_voltage_update(self) -> Tuple[int, float]:
        msg = self._wait_for("node_voltage")

        node_id = int(msg["node_id"])
        voltage = float(msg["voltage"])

        return node_id, voltage

    def on_module_parameters_update(self):
        msg = self._wait_for("module_parameters")

        node_id = int(msg["node_id"])
        module_id = int(msg["module_id"])

        params: Dict[str, Parameter] = {}
        for name, raw in msg["parameters"].items():
            params[name] = Parameter(
                name=name,
                value=float(raw["value"]),
                unit=raw.get("unit", ""),
            )

        return node_id, module_id, params

    # ================= helper =================
    def _wait_for(self, msg_type: str) -> dict:
        """
        Block cho tới khi nhận được message đúng type.
        """
        while True:
            msg = self._queue.get()
            if msg.get("type") == msg_type:
                return msg
