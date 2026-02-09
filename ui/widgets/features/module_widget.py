from PyQt5.QtWidgets import (
    QFrame, QLabel, QVBoxLayout, QHBoxLayout,
    QWidget, QGridLayout
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from ..components.parameter_box_widget import ParameterBoxWidget


class ModuleWidget(QFrame):
    def __init__(self, module_name: str, parent=None):
        super().__init__(parent)

        self.setObjectName("ModuleWidget")

        # ===== Header =====
        self.title = QLabel(module_name)
        self.title.setObjectName("ModuleTitle")

        self.status = QLabel("NORMAL")
        self.status.setObjectName("ModuleStatus")
        self.status.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

        header = QHBoxLayout()
        header.addWidget(self.title)
        header.addStretch()
        header.addWidget(self.status)

        # ===== Parameters area =====
        self.param_container = QWidget()
        self.param_layout = QGridLayout(self.param_container)
        self.param_layout.setSpacing(8)
        self.param_layout.setContentsMargins(4, 4, 4, 4)

        # ===== Main layout =====
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.addLayout(header)
        layout.addWidget(self.param_container)

        self._param_widgets = {}

    # ---------- API ----------
    def set_status(self, status: str):
        self.status.setText(status.upper())
        self.setProperty("status", status.lower())
        self.style().unpolish(self)
        self.style().polish(self)

    def add_parameter(
        self,
        name: str,
        value: str,
        status_color=QColor(0, 200, 0),
        row: int = 0,
        col: int = 0
    ):
        box = ParameterBoxWidget(name, value, status_color)
        self.param_layout.addWidget(box, row, col)
        self._param_widgets[name] = box

    def update_parameter(self, name: str, value: str, status_color: QColor):
        if name not in self._param_widgets:
            return
        box = self._param_widgets[name]
        box.set_value(value)
        box.set_status_color(status_color)
