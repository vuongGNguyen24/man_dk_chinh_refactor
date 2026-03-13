from typing import Literal

from domain.value_objects.bullet_status import BulletStatus
from ui.views import MainTab
from application.services import FiringControlService


class BulletChoiceInputAdapter:
    """
    Inbound Adapter – UI → Application

    Responsibility:
    - Listen to BulletChoiceInputView signals
    - Extract validated input from view
    - Translate UI state into application use-case calls

    This adapter is the only place that depends on PyQt.
    """

    def __init__(
        self,
        view: MainTab,
        service: FiringControlService,
    ):
        self._view = view
        self._service = service

        self._wire()
        
    def _wire(self):
        self._view.bullet_widget.launcher_clicked.connect(self._on_chosen_bullet_clicked)
        self._view.launch_clicked.connect(self._on_launch_clicked)
        self._view.select_all_clicked.connect(self._on_select_all_clicked)
        self._view.unselect_all_clicked.connect(self._on_unselect_all_clicked)
    
    def _on_launch_clicked(self):
        for launcher_id in self._service.launchers.keys():
            self._service.select_bullets(launcher_id=launcher_id)
            
    def _on_chosen_bullet_clicked(self, side: Literal['left', 'right'], index: int):
        state = self._service.launchers[side].get_bullet_status(index)
        if state == BulletStatus.SELECTED:
            self._service.unchoose_bullet(launcher_id=side, index=index)
        else:
            self._service.choose_bullet(launcher_id=side, index=index)
            
    def _on_select_all_clicked(self, launcher_id: Literal["left", "right"]):
        self._service.select_all_bullets(launcher_id)
        
    def _on_unselect_all_clicked(self):
        self._service.unselect_all_bullets()
        