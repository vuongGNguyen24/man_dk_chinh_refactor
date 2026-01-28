from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from typing import List
from module_widget import ModuleWidget
from parameter_box_widget import ParameterBoxWidget

def load_qss(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


class InfoPanelRenderer(QWidget):
    def __init__(self, ui_file_path: str):
        super().__init__()
        loadUi(ui_file_path, self)

        # ===== Load QSS =====
        self.setStyleSheet(
            load_qss("module_style.qss") +
            load_qss("parameter_style.qss")
        )

        # ===== Scroll area setup =====
        self._container = QWidget()
        self._layout = QVBoxLayout(self._container)
        self._layout.setAlignment(Qt.AlignTop)
        self._layout.setSpacing(10)
        self._layout.setContentsMargins(8, 8, 8, 8)

        self.moduleScrollArea.setWidget(self._container)
        self.moduleScrollArea.setWidgetResizable(True)

    # --------------------------------------------------
    # PUBLIC API
    # --------------------------------------------------
    def set_modules(self, modules):
        self._clear_modules()

        for module in modules:
            widget = self._build_module_widget(module)
            self._layout.addWidget(widget)

        self._layout.addStretch()

    # --------------------------------------------------
    # INTERNAL
    # --------------------------------------------------
    def _clear_modules(self):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

    def _build_module_widget(self, module):
        """
        module: ModuleView
        """
        w = ModuleWidget(module.name)
        w.set_status("normal")  # mock, sau map domain thì đổi

        row = col = 0
        for param in module.parameters:
            w.add_parameter(
                name=param.label,
                value=param.display_value,
                status_color=param.status_color,
                row=row,
                col=col
            )

            col += 1
            if col == 4:
                row += 1
                col = 0

        return w

            
            
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from dataclasses import dataclass
    from PyQt5.QtGui import QColor

    @dataclass
    class ParameterView:
        label: str
        display_value: str
        status_color: QColor

    @dataclass
    class ModuleView:
        name: str
        parameters: List[ParameterView]
        
    mock_module = ModuleView(
        name="Module A",
        parameters=[
            ParameterView("Điện áp", "24.1V", QColor(0,255,0)),
            ParameterView("Dòng", "3.2A", QColor(255,0,0)),
            ParameterView("Công suất", "76W", QColor(0,255,0)),
            ParameterView("Nhiệt độ", "45°C", QColor(0,255,0)),
        ]
    )
    
    mock_module2 = ModuleView(
        name="Module B",
        parameters=[
            ParameterView("Điện áp", "24.1V", QColor(0,255,0)),
            ParameterView("Dòng", "3.2A", QColor(255,0,0)),
            ParameterView("Công suất", "76W", QColor(0,255,0)),
            ParameterView("Nhiệt độ", "45°C", QColor(0,255,0)),
        ]
    )
    app = QApplication(sys.argv)
    renderer = InfoPanelRenderer("infor_panel_reader.ui")
    renderer.set_modules([mock_module, mock_module2])
    renderer.show()
    sys.exit(app.exec_())

