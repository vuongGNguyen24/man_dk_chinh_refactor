from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ParameterBoxWidget(QFrame):
    def __init__(self, label: str, value: str = "", status_color=QColor(0, 255, 0), parent=None):
        super().__init__(parent)

        self.setObjectName("ParameterBox")
        self.setFixedHeight(80)

        # ---- label ----
        self.label = QLabel(label)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setObjectName("ParamLabel")

        # ---- status line ----
        self.status_line = QFrame()
        self.status_line.setFixedHeight(2)
        self.status_line.setObjectName("StatusLine")

        # ---- value ----
        self.value = QLabel(value)
        self.value.setAlignment(Qt.AlignCenter)
        self.value.setObjectName("ParamValue")

        # ---- layout ----
        layout = QVBoxLayout(self)
        layout.setSpacing(6)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.addWidget(self.label)
        layout.addWidget(self.status_line)
        layout.addWidget(self.value)

        self.set_status_color(status_color)

    def set_value(self, text: str):
        self.value.setText(text)

    def set_status_color(self, color: QColor):
        self.status_line.setStyleSheet(
            f"background-color: rgb({color.red()}, {color.green()}, {color.blue()});"
        )
