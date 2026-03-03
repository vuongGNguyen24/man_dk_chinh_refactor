from typing import List
from application.ports.ui_firing_output_port import FiringStatusOutputPort, BulletStatus
from application.dto.angle.packet import AnglePacket
from ui.views import MainTab
from ui.widgets.features.compass_widget import AngleCompass
from ui.widgets.features.vertical_compass_widget import VerticalCompassWidget
from ui.views.angle_input.angle_input_view import AngleInputView, ControlMode

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
        
    def on_target_angle_and_distance_changed(self, launcher_id: str, angle: AnglePacket, distance_m: float) -> None:
        self._main_tab.numeric_data_widget.update_data_on_launcher(launcher_id, **{"Góc hướng mục tiêu (độ)": angle.azimuth,
                                                                                   "Góc tầm mục tiêu (độ)": angle.elevation,
                                                                                   "Khoảng cách (m)": distance_m})

        compass: AngleCompass = self._main_tab.compass_left if launcher_id == "left" else self._main_tab.compass_right
        compass.setAimDirection(angle.azimuth)
        
        vertical_compass: VerticalCompassWidget = self._main_tab.half_compass_left if launcher_id == "left" else self._main_tab.half_compass_right
        vertical_compass.setAimDirection(angle.azimuth)
        vertical_compass.setAimAngle(angle.elevation)
        
    def on_current_angle_changed(self, launcher_id: str, angle: AnglePacket) -> None:
        self._main_tab.numeric_data_widget.update_data_on_launcher(launcher_id, **{"Góc hướng hiện tại (độ)": angle.azimuth,
                                                                                   "Góc tầm hiện tại (độ)": angle.elevation})
        
        compass: AngleCompass = self._main_tab.compass_left if launcher_id == "left" else self._main_tab.compass_right
        compass.setCurrentDirection(angle.azimuth)
        
        vertical_compass: VerticalCompassWidget = self._main_tab.half_compass_left if launcher_id == "left" else self._main_tab.half_compass_right
        vertical_compass.setCurrentDirection(angle.azimuth)
        vertical_compass.setCurrentAngle(angle.elevation)
        
    def on_distance_input_changed(self, launcher_id: str, distance_m: float) -> None:
        angle_input_view: AngleInputView = self._main_tab.angle_input_widget_left if launcher_id == "left" else self._main_tab.angle_input_widget_right
        if angle_input_view.distance_control_mode == ControlMode.AUTO:
            angle_input_view.distanceInput.setText(f"{distance_m:.2f}")