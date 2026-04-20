from typing import Dict, List
import json
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from application.dto import ElectricalPointStatus
from application.ports.electrical_circuit import ElectricalPointObserverPort
from ui.views.system_diagram import SystemDiagramView


class SystemDiagramElectricalObserver(QObject, ElectricalPointObserverPort):
    """
    Adapter:
    - Nhận NodeStatus từ application, truyền state vào SystemDiagramView
    """
    sig_points_changed = pyqtSignal(list)

    def __init__(
        self,
        diagram_view: SystemDiagramView,
    ):
        super().__init__()
        self._view = diagram_view
        self.sig_points_changed.connect(self._do_update_points)

    def on_points_changed(self, changed: List[ElectricalPointStatus]) -> None:
        """
        Điểm có điện = OK
        Điểm mất điện = ERROR
        """
        self.sig_points_changed.emit(changed)
        
    @pyqtSlot(list)
    def _do_update_points(self, changed: List[ElectricalPointStatus]) -> None:
        for status in changed:
            self._handle_point(status)
            
    def _handle_point(self, status: ElectricalPointStatus):
        has_error = not status.powered
        self._view.set_connection_state(status.point_id, has_error)
