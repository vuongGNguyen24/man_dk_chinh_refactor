from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from ...helpers.ui_widget_replacer import replace_ui_widget
from ...widgets.features.bullet_widget import BulletWidget
from ...widgets.features.compass_widget import AngleCompass
from ...widgets.features.vertical_compass_widget import VerticalCompassWidget
from ...widgets.components.custom_message_box_widget import ConfirmationWidget
from ...widgets.components.isometric_buttons import SVGIsometricButton, IsometricVisualState
from ...widgets.features.numeric_display_widget import NumericDataWidget
from ..effects.grid_background_renderer import GridBackgroundWidget
from ..angle_input import AngleInputView
from ..ballistic_calculator import BallisticCalculatorWidget
from application.dto.angle.limit import ANGLE_INPUT_VALIDATOR
from ui.styles.isometric_button.praser import IsometricTheme



class MainTab(GridBackgroundWidget):
    # ===== UI intents (signals) =====
    # ok_clicked = QtCore.pyqtSignal()
    cancel_clicked = QtCore.pyqtSignal()
    launch_clicked = QtCore.pyqtSignal()
    calculator_accepted = QtCore.pyqtSignal()
    change_angle_input_clicked = QtCore.pyqtSignal(str)  # "left" | "right"
    cancel_angle_input_clicked = QtCore.pyqtSignal()
    # angle_input_clicked = QtCore.pyqtSignal(str)  # "left" | "right"

    def __init__(self, ui_path:str, parent=None, enable_animation=True):
        super().__init__(parent, enable_animation=enable_animation)
        self.isometric_theme = IsometricTheme("ui/styles/isometric_button/theme.yaml")
        self._load_ui(ui_path)
        self._bind_placeholders()
        self._bind_signals()
    def _load_ui(self, ui_path:str):
        self.ui = loadUi(ui_path, self)
        
    def _bind_placeholders(self):
        ui = self.ui

        self.bullet_widget = replace_ui_widget(
            ui, "bullet_widget", BulletWidget
        )
        self.bullet_widget.update_launcher("left", [True] * 18, {1, 2, 3, 4, 8, 10, 14, 17})
        self.bullet_widget.update_launcher("right", [False] * 18, {1, 2})
        # print(self.bullet_widget._buttons["Giàn trái"][1].fontInfo().pointSize())
        self.compass_left = replace_ui_widget(
            ui, "compass_left",
            AngleCompass, 35, 35, [210, 360], 0
        )

        self.compass_right = replace_ui_widget(
            ui, "compass_right",
            AngleCompass, 45, 40, [180, 330], 0
        )

        self.half_compass_left = replace_ui_widget(
            ui, "half_compass_left",
            VerticalCompassWidget, 15, 20
        )

        self.half_compass_right = replace_ui_widget(
            ui, "half_compass_right",
            VerticalCompassWidget, 30, 25
        )

        self.launch_button = replace_ui_widget(
            self, "ok_button",
            SVGIsometricButton, state=self.isometric_theme("IsometricButton", 'enabled'), svg_path="ui/resources/Icons/launch.svg", icon_size=(70, 70))
        self.cancel_button = replace_ui_widget(
            ui, "cancel_button",
            SVGIsometricButton, state=self.isometric_theme("IsometricButton", 'disabled'), svg_path="ui/resources/Icons/cancel.svg", icon_size=(70, 70))
        self.launch_all_button = replace_ui_widget(
            ui, "launch_all_button",
            SVGIsometricButton, state=self.isometric_theme("IsometricButton", 'disabled'), svg_path="ui/resources/Icons/launch_all.svg", icon_size=(70, 70))
        self.calculator_button = replace_ui_widget(
            ui, "calculator_button",
            SVGIsometricButton, state=self.isometric_theme("IsometricButton", 'enabled'), svg_path="ui/resources/Icons/calculator.svg", icon_size=(75, 75))
        self.numeric_data_widget = replace_ui_widget(
            ui, "numeric_data_widget", NumericDataWidget
        )
        self.angle_input_button_left = ui.findChild(
            QWidget, "angle_input_button_left"
        )
        self.angle_input_button_left.raise_()
        self.angle_input_button_right = ui.findChild(
            QWidget, "angle_input_button_right"
        )
        self.angle_input_button_right.raise_()
        self.angle_input_widget_left = AngleInputView('ui/views/angle_input/angle_input.ui', limits=ANGLE_INPUT_VALIDATOR, side_label="Trái", parent=self)
        self.angle_input_widget_right = AngleInputView('ui/views/angle_input/angle_input.ui', limits=ANGLE_INPUT_VALIDATOR, side_label="Phải", parent=self)
        self.angle_input_widget_left.hide()
        self.angle_input_widget_right.hide()
        
        self.calculator_widget = BallisticCalculatorWidget(parent=self, ui_path="ui/views/ballistic_calculator/ballistic_calculator.ui")
        self.calculator_widget.hide()
        
        self.cofimation_widget = ConfirmationWidget(parent=self)
        self.cofimation_widget.hide()
    # -------------------------------------------------
    # Signal binding
    # -------------------------------------------------
    def _bind_signals(self):
        self.launch_button.clicked.connect(self.on_launch_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)
        self.launch_all_button.clicked.connect(self.on_launch_all_clicked)
        
        self.calculator_button.clicked.connect(self.on_calculator_clicked)
        self.calculator_widget.accepted.connect(self.on_calculator_accepted)
        self.calculator_widget.canceled.connect(self.on_calculator_canceled)
        
        self.angle_input_button_left.clicked.connect(
            lambda: self.on_angle_input_clicked("left")
        )
        self.angle_input_button_right.clicked.connect(
            lambda: self.on_angle_input_clicked("right")
        )
        self.angle_input_widget_left.accepted.connect(lambda: self.on_angle_input_accepted("left"))
        self.angle_input_widget_right.accepted.connect(lambda: self.on_angle_input_accepted("right"))
        self.angle_input_widget_left.rejected.connect(lambda: self.on_angle_input_rejected("left"))
        self.angle_input_widget_right.rejected.connect(lambda: self.on_angle_input_rejected("right"))
        self.cofimation_widget.confirmed.connect(self.launch_clicked.emit)
    
    def on_launch_clicked(self):
        self.cofimation_widget.show_confirmation("Thông báo", "Bạn có chắc chắn muốn chọn đạn")
    
    def on_launch_all_clicked(self):
        #chọn hết tất cả đạn đang có
        
        self.on_launch_clicked()
        
    def on_angle_input_clicked(self, direction: str):
        print(direction)
        if direction == "left":
            self.angle_input_widget_left.show()
        elif direction == "right":
            self.angle_input_widget_right.show()
    
    def hide_angle_input(self):
        self.angle_input_widget_left.hide()
        self.angle_input_widget_right.hide()
        
    def on_angle_input_accepted(self, direction: str):
        #TO DO: emit data to main
        self.hide_angle_input()
        
    def on_angle_input_rejected(self, direction: str):
        self.hide_angle_input()
    
    def on_calculator_clicked(self):
        self.calculator_widget.show()
        print("calculator clicked")
        
    def on_calculator_accepted(self):
        self.calculator_widget.hide()
        self.calculator_accepted.emit()
        print("calculator accepted")
        
    def on_calculator_canceled(self):
        self.calculator_widget.hide()
        print("calculator canceled")
    # -------------------------------------------------
    # UI update methods (NO business logic)
    # -------------------------------------------------
    def update_compass(self, left, right):
        self.compass_left.update_angle(**left)
        self.compass_right.update_angle(**right)

    def update_half_compass(self, left, right):
        self.half_compass_left.update_angle(**left)
        self.half_compass_right.update_angle(**right)

    def update_bullet_state(self, left_status, right_status):
        self.bullet_widget.update_launcher("Giàn trái", left_status)
        self.bullet_widget.update_launcher("Giàn phải", right_status)

    def clear_selection(self):
        self.bullet_widget.left_selected_launchers.clear()
        self.bullet_widget.right_selected_launchers.clear()
        

if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys
    app = QApplication(sys.argv)
    main_tab = MainTab(ui_path="ui/views/main_tab/main_control_tab.ui")
    colors = {
        "ready": QColor(0, 200, 0),
        "selected": QColor(0, 255, 0),
        "disabled": QColor(128, 128, 128),
        "border": QColor(80, 80, 80),
        "text": QColor(255, 255, 255),
    }
    import random
    main_tab.bullet_widget.update_launcher("Giàn trái", [random.choice([True, False]) for _ in range(18)], {1, 2})
    main_tab.bullet_widget.update_launcher("Giàn phải", [random.choice([True, False]) for _ in range(18)], {1, 2})
    # main_tab.update_compass(left=0, right=0)
    # main_tab.update_half_compass(left=0, right=0)
    # main_tab.update_bullet_state(left_status=)
    main_tab.show()
    sys.exit(app.exec_())
