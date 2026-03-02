from typing import List
from application.ports.ui_firing_output_port import FiringStatusOutputPort, BulletStatus
from ui.views import MainTab


class FiringWidgetAdapter(FiringStatusOutputPort):

    def __init__(self, main_tab: MainTab):
        self._main_tab = main_tab

    def on_bullet_status_changed(self, launcher_id: str, statuses: List[BulletStatus]) -> None:
        selected = set()
        for status in statuses:
            if status == BulletStatus.SELECTED:
                selected.add(status.index)
        bool_status = [status != BulletStatus.EMPTY for status in statuses]
        
        self._main_tab.bullet_widget.update_launcher(launcher_id, bool_status, selected)
        self._main_tab.numeric_data_widget.update_data_on_launcher(launcher_id, **{"Pháo sẵn sàng": sum(bool_status),
                                                                                   "Pháo đã chọn": len(selected)})
        
            