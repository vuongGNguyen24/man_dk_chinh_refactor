
from typing import Dict, List, Optional

from application.dto import ElectricalPointStatus
from application.ports.electrical_circuit import ElectricalPointInputPort, ElectricalPointObserverPort


class ElectricalPointMonitorService:
    def __init__(
        self,
        input_port: ElectricalPointInputPort,
        observer: Optional[ElectricalPointObserverPort] = None,
    ):
        self._input = input_port
        self._observer = observer

        # state hiện tại trong application
        self._current: Dict[str, bool] = {}

    def poll(self) -> List[ElectricalPointStatus]:
        """
        Được gọi định kỳ (timer, loop).
        Trả về danh sách các điểm bị thay đổi.
        """
        new_snapshot = self._input.read_points()
        changed = self._diff(new_snapshot)

        if changed and self._observer:
            self._observer.on_points_changed(changed)

        return changed

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
