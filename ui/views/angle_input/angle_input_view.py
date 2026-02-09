from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator


from ui.widgets.components.input_type_widget import ToggleAngleInputWidget
from dataclasses import dataclass
from typing import Optional
from enum import Enum
import ui.helpers.qss as qss
from ui.helpers.ui_widget_replacer import replace_ui_widget
from application.dto import AngleInputValidator

class ControlMode:
    AUTO = 0
    MANUAL = 1
    
class InputType:
    DISTANCE = 0
    ELEVATOR = 1

class AngleInputView(QWidget):
    accepted = pyqtSignal()
    rejected = pyqtSignal()

    def __init__(
        self,
        ui_path: str,
        limits: AngleInputValidator,
        side_label: str,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)
        loadUi(ui_path, self)  # load UI
        self.use_high_table = False
        self.side_label = side_label
        self.limits = limits
        self._setup_roles()
        self.direction_control_mode = ControlMode.AUTO
        self.distance_control_mode = ControlMode.AUTO
        self.set_validators(limits)

        self._connect_signals()
        
        self._apply_distance_input_ui()
        self._apply_direction_control_mode_ui()
        # self._apply_distance_and_elevation_control_mode_ui()
        
    
    def _connect_signals(self):
        # ---- Toggle clusters ----
        self.modeInputContainer.changed_mode.connect(self._on_input_type_changed)
        self.modeButtonContainer.changed_mode.connect(self._on_distance_and_elevator_mode_changed)        
        self.directionModeButton.changed_mode.connect(self._on_direction_mode_changed)

        # ---- Buttons ----
        self.okButton.clicked.connect(self.accepted.emit)
        self.cancelButton.clicked.connect(self.rejected.emit)

        # ---- Inputs ----
        self.distanceInput.textChanged.connect(self._on_primary_input_changed)
    
    def _setup_roles(self):
        self.modeInputContainer = replace_ui_widget(self, 'modeInputContainer', ToggleAngleInputWidget, 
                          text_labels=["Nhập: Khoảng cách", "Nhập: Góc tầm trực tiếp"], button_text=["Chuyển sang Góc tầm", "Chuyển sang Khoảng cách"])
        self.modeButtonContainer = replace_ui_widget(self, 'modeButtonContainer', ToggleAngleInputWidget,
                          text_labels=["Chế độ: tự động", "Chế độ: thủ công"], button_text=["Chuyển sang thủ công", "Chuyển sang tự động"])
        self.directionModeButton = replace_ui_widget(self, 'directionModeButton', ToggleAngleInputWidget,
                          text_labels=["Chế độ: tự động", "Chế độ: thủ công"], button_text=["Chuyển sang thủ công", "Chuyển sang tự động"])
        
        # ================= OVERLAY & CONTAINER =================
        qss.set_multiple_property(self, role="angle-input", variant="overlay")
        qss.set_multiple_property(self.dialogContainer, role="angle-input", variant="container")

        # ================= TITLE =================
        qss.set_multiple_property(self.titleLabel, role="angle-input", variant="container")

        # ================= GROUP BOXES =================
        for gb in (
            self.distanceGroup,
            self.elevationPreviewGroup,
            self.directionGroup,
        ):
            qss.set_multiple_property(gb, role="angle-input")

        print(f"{self.inputTypeLabel.styleSheet()=}")

        # ================= PREVIEW HEADERS =================
        for lbl in (
            self.decimalLabel,
            self.dmsLabel,
            self.distanceValueLabel
        ):
            qss.set_multiple_property(lbl, role="angle-input", variant="preview-header")
        qss.set_multiple_property(self.tableSelectionLabel, role="angle-input", variant="sub-section")
        # ================= PREVIEW VALUES =================
        for lbl in (
            self.elevationDecimalLabel,
            self.elevationDmsLabel,
            self.distancePreviewLabel
            
        ):
            qss.set_multiple_property(lbl, role="angle-input", variant="preview-value")

        # ================= INPUTS =================
        for inp in (
            self.distanceInput,
            self.directionInput,
            self.elevationInput
        ):
            qss.set_multiple_property(inp, role="angle-input")

       
        qss.set_multiple_property(self.okButton, role="angle-input", variant="confirm")

        qss.set_multiple_property(self.cancelButton, role="angle-input", variant="cancel")

        for rb in (self.lowTableRadio,self.highTableRadio,):
            qss.set_multiple_property(rb, role="angle-input")

        # ================= TRANSPARENT CONTAINERS =================
        for w in (
            self.modeButtonContainer,
            self.tableSelectionContainer,
        ):
            qss.set_multiple_property(w, role="angle-input", variant="transparent")


    def set_validators(self, limits: AngleInputValidator):
        self.__set_validators(limits)
        self._init_text(limits)
    
    def __set_validators(self, limits: AngleInputValidator):
        self.limits = limits
        
        self.distanceInput.setValidator(
            QDoubleValidator(limits.distance.min_normal, limits.distance.max_normal, 1)
        )

        self.directionInput.setValidator(
            QDoubleValidator(limits.azimuth.min_normal, limits.azimuth.max_normal, 1)
        )
        
        self.elevationInput.setValidator(
            QDoubleValidator(limits.elevation.min_normal, limits.elevation.max_normal, 1)
        )
        
        
    def _init_text(self, limits: AngleInputValidator):
        self.titleLabel.setText(f"Nhập góc - Giàn {self.side_label}")
        self.distanceInput.setPlaceholderText(f"Nhập khoảng cách ({self.limits.distance.min_normal} → {self.limits.distance.max_normal})")
        self.elevationInput.setPlaceholderText(f"Nhập góc tầm ({self.limits.azimuth.min_normal} → {self.limits.azimuth.max_normal})")
        self.directionInput.setPlaceholderText(
            f"Nhập góc hướng ({self.limits.azimuth.min_normal} → {self.limits.azimuth.max_normal})"
        )
    

    def _apply_distance_input_ui(self):
        self.elevationInput.hide()
        self.distanceInput.show()
        self.elevationContainer.hide()
        self.tableSelectionContainer.hide()
        self.distanceValueContainer.show()
        self.elevationPreviewGroup.setTitle("Khoảng cách bắn được")
        self._apply_distance_and_elevation_control_mode_ui()
    def _apply_elevation_input_ui(self):
        self.elevationInput.show()
        self.distanceInput.hide()
        self.elevationContainer.show()
        self.tableSelectionContainer.show()
        self.distanceValueContainer.hide()
        self.elevationPreviewGroup.setTitle("Góc tầm tính toán")
        self._apply_distance_and_elevation_control_mode_ui()
    def _apply_direction_control_mode_ui(self):
        is_auto = self.direction_control_mode == ControlMode.AUTO
        self.directionInput.setEnabled(not is_auto)

    def _apply_distance_and_elevation_control_mode_ui(self):
        is_auto = self.distance_control_mode == ControlMode.AUTO
        if self.modeInputContainer.mode == InputType.DISTANCE:
            self.distanceInput.setEnabled(not is_auto)
        else:
            self.elevationInput.setEnabled(not is_auto)
    
    def _on_input_type_changed(self, mode: int):
        if mode == InputType.DISTANCE:
            self._apply_distance_input_ui()
        else:
            self._apply_elevation_input_ui()
    
    def _on_distance_and_elevator_mode_changed(self, mode: int):
        self.distance_control_mode = mode
        self._apply_distance_and_elevation_control_mode_ui()
    
    def _on_direction_mode_changed(self, mode: int):
        self.direction_control_mode = mode
        self._apply_direction_control_mode_ui()
        
    def _on_toggle_input_type(self):
        self.input_type = (
            InputType.ELEVATOR
            if self.input_type == InputType.DISTANCE
            else InputType.DISTANCE
        )
        self.apply_ui_state()

    def _on_toggle_control_mode(self):
        self.control_mode = (
            ControlMode.MANUAL
            if self.control_mode == ControlMode.AUTO
            else ControlMode.AUTO
        )
        self.apply_ui_state()

    def _on_primary_input_changed(self, text: str):
        """Pure view reaction. No calculation here."""
        if not text:
            self.elevationDecimalLabel.setText("--")
            self.distancePreviewLabel.setText("--")
    
    



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from dataclasses import dataclass
    from PyQt5.QtGui import QColor
    from domain.value_objects.angle_handler import AngleThreshold
    from domain.value_objects.parameter import Threshold
    from ui.helpers.qss import load_app_qss
    app = QApplication(sys.argv)
    load_app_qss(app, ["ui/styles/base.qss", "ui/styles/angle_input_dialog.qss"])
    view = AngleInputView(
        ui_path="ui/views/angle_input/a.ui",
        limits=AngleInputValidator(
            elevation=AngleThreshold(10, 60),
            azimuth=AngleThreshold(60, 65),
            distance=Threshold(0, 10000)),
            side_label="Trái")
    view.show()
    sys.exit(app.exec_())