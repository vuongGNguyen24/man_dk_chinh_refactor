
from typing import Dict, List, Optional, Set

from application.dto import ElectricalPointStatus
from application.ports.electrical_circuit import ElectricalPointInputPort, ElectricalPointObserverPort


class ElectricalPointMonitorService:
    def __init__(
        self,
        observer: Optional[ElectricalPointObserverPort] = None,
        ownership: Dict[str, Set[str]] = {},
        debug: bool = False,
    ):
        self._observer = observer

        # state hiện tại trong application
        self._current: Dict[str, bool] = {}
        self._ownership: Dict[str, Set[str]] = ownership
        self._debug = debug
    def on_rs485_snapshot(self, snapshot: Dict[str, bool]):
        if self._debug:
            print("RS485 snapshot")
            print(snapshot)
        self._handle_snapshot(snapshot, self._ownership.get("rs485", set()))
    
    def on_udp_snapshot(self, snapshot: Dict[str, bool]):
        if self._debug:
            print("UDP snapshot")
            print(snapshot)
        self._handle_snapshot(snapshot, self._ownership.get("udp", set()))
        
    def _handle_snapshot(self, snapshot: Dict[str, bool], allowed_points: Set[str]):
        if allowed_points:
            for pid in snapshot.keys():
                if pid not in allowed_points:
                    snapshot.pop(pid)
                
        changed = self._diff(snapshot)
        if changed and self._observer:
            self._observer.on_points_changed(changed)

    def get_state(self, point_id: str) -> bool:
        return self._current.get(point_id, False)

    def get_all_states(self) -> Dict[str, bool]:
        return dict(self._current)

    def _diff(
        self, new_snapshot: Dict[str, bool]
    ) -> List[ElectricalPointStatus]:
        changes: List[ElectricalPointStatus] = []

        for pid, powered in new_snapshot.items():
            old = self._current.get(pid)
            if old is None or old != powered:
                changes.append(
                    ElectricalPointStatus(pid, powered)
                )

        # cập nhật state sau khi diff
        self._current = dict(new_snapshot)
        return changes
