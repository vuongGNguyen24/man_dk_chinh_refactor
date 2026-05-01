from typing import List
from PyQt5.QtCore import QObject, pyqtSignal, pyqtSlot

from application.ports.ui_firing_output_port import FiringStatusOutputPort, BulletStatus
from application.dto.angle.packet import AnglePacket
from ui.views import MainTab
from ui.widgets.features.compass_widget import AngleCompass
from ui.widgets.features.vertical_compass_widget import VerticalCompassWidget
from ui.views.angle_input.angle_input_view import AngleInputView, ControlMode
from ui.styles.isometric_button import IsometricTheme

theme = IsometricTheme("ui/styles/isometric_button/theme.yaml")


class FiringWidgetAdapter(QObject, FiringStatusOutputPort):
    sig_bullet_status_changed = pyqtSignal(str, list)
    sig_target_angle_and_distance_changed = pyqtSignal(str, object, float)
    sig_current_angle_changed = pyqtSignal(str, object)
    sig_distance_input_changed = pyqtSignal(str, float)
    sig_disable_launcher = pyqtSignal(str)
    
    def __init__(self, main_tab: MainTab):
        super().__init__()
        self._main_tab = main_tab
        self.launcher_ids = ["left", "right"]

        self.sig_bullet_status_changed.connect(self._do_update_bullet_status)
        self.sig_target_angle_and_distance_changed.connect(self._do_update_target_angle_and_distance)
        self.sig_current_angle_changed.connect(self._do_update_current_angle)
        self.sig_distance_input_changed.connect(self._do_update_distance_input)
        self.sig_disable_launcher.connect(self._do_disable_launcher)
        
    def on_bullet_status_changed(self, launcher_id: str, statuses: List[BulletStatus]) -> None:
        self.sig_bullet_status_changed.emit(launcher_id, statuses)

    def on_target_angle_and_distance_changed(self, launcher_id: str, angle: AnglePacket, distance_m: float) -> None:
        self.sig_target_angle_and_distance_changed.emit(launcher_id, angle, distance_m)
        
    def on_current_angle_changed(self, launcher_id: str, angle: AnglePacket) -> None:
        self.sig_current_angle_changed.emit(launcher_id, angle)
        
    def on_distance_input_changed(self, launcher_id: str, distance_m: float) -> None:
        self.sig_distance_input_changed.emit(launcher_id, distance_m)

    def disable_launcher(self, launcher_id: str):
        self.sig_disable_launcher.emit(launcher_id)
        
    @pyqtSlot(str)
    def _do_disable_launcher(self, launcher_id: str):
        self._main_tab.disable_launcher(launcher_id)
    
    @pyqtSlot(str, list)
    def _do_update_bullet_status(self, launcher_id: str, statuses: List[BulletStatus]) -> None:
        selected = set()
        bool_status = []
        for index, status in enumerate(statuses):
            index += 1
            if status.is_selected:
                selected.add(index)
            if status.is_loaded:
                bool_status.append(True)
            else:
                bool_status.append(False)
        self._main_tab.bullet_widget.update_launcher(launcher_id, bool_status, selected)
        self._main_tab.numeric_data_widget.update_data_on_launcher(
            launcher_id, 
            **{
                "Pháo sẵn sàng": sum([1 for status in statuses if status.is_loaded]),
                "Pháo đã chọn": len(selected)
            }
        )

    @pyqtSlot(str, object, float)
    def _do_update_target_angle_and_distance(self, launcher_id: str, angle: AnglePacket, distance_m: float) -> None:
        self._main_tab.numeric_data_widget.update_data_on_launcher(
            launcher_id, 
            **{
                "Góc hướng mục tiêu (độ)": angle.azimuth,
                "Góc tầm mục tiêu (độ)": angle.elevation,
                "Khoảng cách (m)": distance_m
            }
        )

        compass: AngleCompass = self._main_tab.compass_left if launcher_id == "left" else self._main_tab.compass_right
        compass.setAimDirection(angle.azimuth)
        
        vertical_compass: VerticalCompassWidget = self._main_tab.half_compass_left if launcher_id == "left" else self._main_tab.half_compass_right
        vertical_compass.setAimDirection(angle.azimuth)
        vertical_compass.setAimAngle(angle.elevation)
        
        #TODO: separate to ballistic calculator outbound adapter
        if launcher_id == 'left':
            self._main_tab.calculator_widget.defaultElevationLeft.setText(f"{angle.elevation:.2f}°")
            self._main_tab.calculator_widget.defaultDirectionLeft.setText(f'{angle.azimuth:.2f}°')
        else:
            self._main_tab.calculator_widget.defaultElevationRight.setText(f"{angle.elevation:.2f}°")
            self._main_tab.calculator_widget.defaultDirectionRight.setText(f'{angle.azimuth:.2f}°')
        
    @pyqtSlot(str, object)
    def _do_update_current_angle(self, launcher_id: str, angle: AnglePacket) -> None:
        #TO DO: change validate to app layer
        # if 10 <= angle.elevation <= 70 and -70 <= angle.azimuth <= 70:
        self._main_tab.numeric_data_widget.update_data_on_launcher(
            launcher_id, 
            **{
                "Góc hướng hiện tại (độ)": angle.azimuth,
                "Góc tầm hiện tại (độ)": angle.elevation
            }
        )
        
        compass: AngleCompass = self._main_tab.compass_left if launcher_id == "left" else self._main_tab.compass_right
        compass.setCurrentDirection(angle.azimuth)
        
        vertical_compass: VerticalCompassWidget = self._main_tab.half_compass_left if launcher_id == "left" else self._main_tab.half_compass_right
        vertical_compass.setCurrentDirection(angle.azimuth)
        vertical_compass.setCurrentAngle(angle.elevation)
        
    @pyqtSlot(str, float)
    def _do_update_distance_input(self, launcher_id: str, distance_m: float) -> None:
        angle_input_view: AngleInputView = self._main_tab.angle_input_widget_left if launcher_id == "left" else self._main_tab.angle_input_widget_right
        if angle_input_view.distance_control_mode == ControlMode.AUTO:
            angle_input_view.distanceInput.setValue(distance_m)