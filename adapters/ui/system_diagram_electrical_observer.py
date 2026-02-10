from typing import Dict, List
import json

from application.dto import ElectricalPointStatus
from application.ports.electrical_circuit import ElectricalPointObserverPort
from ui.views.system_diagram import SystemDiagramView


class SystemDiagramElectricalObserver(ElectricalPointObserverPort):
    """
    Adapter:
    - Nhận NodeStatus từ application, truyền state vào SystemDiagramView
    """

    def __init__(
        self,
        diagram_view: SystemDiagramView,
    ):
        self._view = diagram_view

    def on_points_changed(self, changed: List[ElectricalPointStatus]) -> None:
        """
        Điểm có điện = OK
        Điểm mất điện = ERROR
        """
        for status in changed:
            self._handle_point(status)
            
    def _handle_point(self, status: ElectricalPointStatus):
        has_error = not status.powered
        self._view.set_connection_state(status.point_id, has_error)
