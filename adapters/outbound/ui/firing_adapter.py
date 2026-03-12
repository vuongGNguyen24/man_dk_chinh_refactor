from typing import List
from application.ports.ui_firing_output_port import FiringStatusOutputPort, BulletStatus
from application.dto.angle.packet import AnglePacket
from ui.views import MainTab
from ui.widgets.features.compass_widget import AngleCompass
from ui.widgets.features.vertical_compass_widget import VerticalCompassWidget
from ui.views.angle_input.angle_input_view import AngleInputView, ControlMode
from ui.styles.isometric_button import IsometricTheme
theme = IsometricTheme("ui/styles/isometric_button/theme.yaml")
class FiringWidgetAdapter(FiringStatusOutputPort):

    def __init__(self, main_tab: MainTab):
        self._main_tab = main_tab
        self.launcher_ids = ["left", "right"]
    def on_bullet_status_changed(self, launcher_id: str, statuses: List[BulletStatus]) -> None:
        # print(statuses)
        selected = set()
        bool_status = []
        for index, status in enumerate(statuses):
            index += 1
            if status == BulletStatus.SELECTED:
                selected.add(index)
            if status != BulletStatus.EMPTY:
                bool_status.append(True)
            else:
                bool_status.append(False)
        # print(bool_status)
        self._main_tab.bullet_widget.update_launcher(launcher_id, bool_status, selected)
        self._main_tab.numeric_data_widget.update_data_on_launcher(launcher_id, **{"Pháo sẵn sàng": sum([1 for status in statuses if status != BulletStatus.EMPTY]),
                                                                                   "Pháo đã chọn": len(selected)})
        num_loaded_left_bullet = int(self._main_tab.numeric_data_widget.get_data("left", "Pháo sẵn sàng"))
        num_loaded_right_bullet = int(self._main_tab.numeric_data_widget.get_data("right", "Pháo sẵn sàng"))
        num_selected_bullet = int(self._main_tab.numeric_data_widget.get_data("left", "Pháo đã chọn")) + int(self._main_tab.numeric_data_widget.get_data("right", "Pháo đã chọn"))
        self._main_tab.launch_left_button.apply_visual_state(theme("IsometricButton", 'function_enabled' if num_loaded_left_bullet > 0 else 'disabled'))
        self._main_tab.launch_right_button.apply_visual_state(theme("IsometricButton", 'function_enabled' if num_loaded_right_bullet > 0 else 'disabled'))
        self._main_tab.cancel_button.apply_visual_state(theme("IsometricButton", 'function_enabled' if num_selected_bullet > 0 else 'disabled'))
    def on_target_angle_and_distance_changed(self, launcher_id: str, angle: AnglePacket, distance_m: float) -> None:
        print(distance_m)
        self._main_tab.numeric_data_widget.update_data_on_launcher(launcher_id, **{"Góc hướng mục tiêu (độ)": angle.azimuth,
                                                                                   "Góc tầm mục tiêu (độ)": angle.elevation,
                                                                                   "Khoảng cách (m)": distance_m})

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