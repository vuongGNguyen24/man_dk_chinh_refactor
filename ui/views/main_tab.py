from PyQt5 import QtCore
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi
from ..helpers.ui_widget_replacer import replace_ui_widget
from ..widgets.features.bullet_widget import BulletWidget
from ..widgets.features.compass_widget import AngleCompass
from ..widgets.features.vertical_compass_widget import VerticalCompassWidget
from ..widgets.components.isometric_buttons import SVGIsometricButton, IsometricVisualState
from ..widgets.features.numeric_display_widget import NumericDataWidget
from .effects.grid_background_renderer import GridBackgroundWidget

DEFAULT_ISO_ENABLED = IsometricVisualState(
    top_color=QColor("#30ffffff"),
    border_color=QColor("#30ffffff"),
    text_color=QColor("#ffffff"),
    depth=6.0,
    enabled=True,
)

DEFAULT_ISO_DISABLED = IsometricVisualState(
    top_color=QColor("#121212"),
    border_color=QColor("#30ffffff"),
    text_color=QColor("#888888"),
    depth=6.0,
    enabled=False,
)


class MainTabView(GridBackgroundWidget):
    # ===== UI intents (signals) =====
    ok_clicked = QtCore.pyqtSignal()
    cancel_clicked = QtCore.pyqtSignal()
    launch_all_clicked = QtCore.pyqtSignal()
    calculator_clicked = QtCore.pyqtSignal()
    angle_input_clicked = QtCore.pyqtSignal(str)  # "left" | "right"

    def __init__(self, ui_path:str, parent=None, enable_animation=True):
        super().__init__(parent, enable_animation=enable_animation)

        self._load_ui(ui_path)
        self._bind_placeholders()
        self._bind_signals()

    # -------------------------------------------------
    # UI loading
    # -------------------------------------------------
    def _load_ui(self, ui_path:str):
        self.ui = loadUi(ui_path, self)

    # -------------------------------------------------
    # UI binding
    # -------------------------------------------------
    def _bind_placeholders(self):
        ui = self.ui

        self.bullet_widget = replace_ui_widget(
            ui, "bullet_widget", BulletWidget
        )

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

        self.ok_button = replace_ui_widget(
            self, "ok_button",
            SVGIsometricButton, state=DEFAULT_ISO_ENABLED, svg_path="ui/resources/Icons/launch.svg")
        self.cancel_button = replace_ui_widget(
            ui, "cancel_button",
            SVGIsometricButton, state=DEFAULT_ISO_ENABLED, svg_path="ui/resources/Icons/cancel.svg")
        self.launch_all_button = replace_ui_widget(
            ui, "launch_all_button",
            SVGIsometricButton, state=DEFAULT_ISO_ENABLED, svg_path="ui/resources/Icons/launch_all.svg")
        self.calculator_button = replace_ui_widget(
            ui, "calculator_button",
            SVGIsometricButton, state=DEFAULT_ISO_ENABLED, svg_path="ui/resources/Icons/calculator.svg")
        self.numeric_data_widget = replace_ui_widget(
            ui, "numeric_data_widget", NumericDataWidget
        )
        self.angle_input_button_left = ui.findChild(
            QWidget, "angle_input_button_left"
        )
        self.angle_input_button_right = ui.findChild(
            QWidget, "angle_input_button_right"
        )

    # -------------------------------------------------
    # Signal binding
    # -------------------------------------------------
    def _bind_signals(self):
        self.ok_button.clicked.connect(self.ok_clicked)
        self.cancel_button.clicked.connect(self.cancel_clicked)
        self.launch_all_button.clicked.connect(self.launch_all_clicked)
        self.calculator_button.clicked.connect(self.calculator_clicked)

        self.angle_input_button_left.clicked.connect(
            lambda: self.angle_input_clicked.emit("left")
        )
        self.angle_input_button_right.clicked.connect(
            lambda: self.angle_input_clicked.emit("right")
        )

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
    main_tab = MainTabView(ui_path="ui/views/main_control_tab.ui")
    colors = {
        "ready": QColor(0, 200, 0),
        "selected": QColor(0, 255, 0),
        "disabled": QColor(128, 128, 128),
        "border": QColor(80, 80, 80),
        "text": QColor(255, 255, 255),
    }
    import random
    main_tab.bullet_widget.update_launcher("Giàn trái", [random.choice([True, False]) for _ in range(18)], {1, 2}, colors=colors)
    main_tab.bullet_widget.update_launcher("Giàn phải", [random.choice([True, False]) for _ in range(18)], {1, 2}, colors=colors)
    # main_tab.update_compass(left=0, right=0)
    # main_tab.update_half_compass(left=0, right=0)
    # main_tab.update_bullet_state(left_status=)
    main_tab.show()
    sys.exit(app.exec_())
