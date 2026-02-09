from typing import List
from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QHBoxLayout, QSizePolicy
from PyQt5.QtCore import pyqtSignal

import ui.helpers.qss as qss
class ToggleAngleInputWidget(QWidget):
    changed_mode = pyqtSignal(int)

    def __init__(
        self,
        text_labels: List[str],
        button_text: List[str],
        parent=None,
    ):
        super().__init__(parent)

        self.mode: int = 0
        if len(text_labels) != len(button_text):
            raise ValueError("text_labels and button_text must have same length")
        self.text_labels = text_labels
        self.button_text = button_text
        self.num_mode = len(text_labels)
        self._build_ui()
        self._change_text()

        self.toggle_btn.clicked.connect(self._on_toggle_btn_clicked)

    # ---------------- UI ----------------

    def _build_ui(self):
        self.setMinimumSize(500, 60)

        self.label = QLabel(self)
        qss.set_multiple_property(self.label, role="angle-input", variant="section")

        self.toggle_btn = QPushButton(self)
        qss.set_multiple_property(self.toggle_btn, role="angle-input")
        self.label.setMinimumHeight(45)
        self.label.setMaximumHeight(45)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        self.toggle_btn.setMinimumHeight(45)
        self.toggle_btn.setMaximumHeight(45)
        self.toggle_btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)

        layout.addWidget(self.label)
        layout.addWidget(self.toggle_btn)

    def _change_text(self):
        
        self.label.setText(self.text_labels[self.mode])
        self.toggle_btn.setText(self.button_text[self.mode])
   
    def _on_toggle_btn_clicked(self):
        self.mode = (self.mode + 1) % self.num_mode
        self._change_text()
        self.changed_mode.emit(self.mode)
        
        
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    import ui.helpers.qss as qss
    app = QApplication(sys.argv)
    qss.load_app_qss(app, ["ui/styles/angle_input_dialog.qss"])
    widget = ToggleAngleInputWidget(
        text_labels=["Góc tầm", "Khoảng cách"],
        button_text=["Chuyển sang Góc tầm", "Chuyển sang Khoảng cách"],
    )
    widget.show()
    sys.exit(app.exec_())
