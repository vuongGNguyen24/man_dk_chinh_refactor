from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

from ui.views.effects.grid_background_renderer import GridBackgroundWidget
from ui.views.system_diagram.system_diagram_view import SystemDiagramView
from ui.views.info_view.info_panel_renderer import InfoPanelRenderer
from ui.widgets.components.status_indicator_widget import StatusIndicatorWidget
from application.services.system_monitor_service import SystemMonitorService
class InfoTab(GridBackgroundWidget):
    """
    Coordinator cho tab Hệ thống (refactored)
    """

    def __init__(self, parent=None):
        super().__init__(
            parent,
            enable_animation=True
        )


        # ===== Layout =====
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # ===== System diagram =====
        self.diagram = SystemDiagramView(
            ui_file="ui/views/system_diagram/layout/system_diagram.ui",
            fps=20,
        )
        layout.addWidget(self.diagram, stretch=3)

        # ===== Info panel =====
        self.info_panel = InfoPanelRenderer(
            r"ui\views\info_view\infor_panel_reader.ui"
        )
        self.info_panel.hide()
        layout.addWidget(self.info_panel, stretch=2)

        self.status_indicator = StatusIndicatorWidget(self)
        self.status_indicator.show()

        
        # ===== Signals =====
        self.diagram.selected_node.connect(self._on_node_selected)
        self.setProperty("role", "dialog")
        self.setProperty("variant", "confirm")
        
    def resizeEvent(self, event):
        super().resizeEvent(event)

        margin = 20
        w = self.status_indicator.width()
        h = self.status_indicator.height()

        self.status_indicator.setGeometry(
            margin,
            self.height() - h - margin,
            w,
            h
        )

    # --------------------------------------------------
    # Slots
    # --------------------------------------------------
    def _on_node_selected(self, node_id: str):
        """
        Khi user click vào node trong sơ đồ
        """
        print(node_id)
        node_data = self.system_data_manager.get_node(node_id)
        if not node_data:
            return

        modules = self._map_node_to_modules(node_data)

        self.info_panel.set_modules(modules)
        self.info_panel.show()

    # --------------------------------------------------
    # Mapping layer (Adapter)
    # --------------------------------------------------
    def _map_node_to_modules(self, node_data):
        """
        Domain → ViewModel
        Trả về List[ModuleView]
        """
        modules = []
        for module in node_data.modules:
            modules.append(module.to_view())
        return modules


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from dataclasses import dataclass
    from PyQt5.QtGui import QColor
    from typing import List
    from ui.helpers.qss import load_app_qss
    @dataclass
    class ParameterView:
        label: str
        display_value: str
        status_color: QColor

    @dataclass
    class ModuleView:
        name: str
        parameters: List[ParameterView]

    @dataclass
    class NodeData:
        modules: List[ModuleView]

    class FakeSystemDataManager:
        def __init__(self):
            self.nodes = {
                "node_1": NodeData(
                    modules=[
                        ModuleView(
                            name="Module A",
                            parameters=[
                                ParameterView("Điện áp", "24.1V", QColor(0, 255, 0)),
                                ParameterView("Dòng", "3.2A", QColor(255, 0, 0)),
                                ParameterView("Công suất", "76W", QColor(0, 255, 0)),
                                ParameterView("Nhiệt độ", "45°C", QColor(0, 255, 0)),
                            ],
                        ),
                        ModuleView(
                            name="Module B",
                            parameters=[
                                ParameterView("Điện áp", "24.1V", QColor(0, 255, 0)),
                                ParameterView("Dòng", "3.2A", QColor(255, 0, 0)),
                                ParameterView("Công suất", "76W", QColor(0, 255, 0)),
                                ParameterView("Nhiệt độ", "45°C", QColor(0, 255, 0)),
                            ],
                        ),
                    ]
                ),
                "node_2": NodeData(
                    modules=[
                        ModuleView(
                            name="Module A",
                            parameters=[
                                ParameterView("Điện áp", "24.1V", QColor(0, 255, 0)),
                                ParameterView("Dòng", "3.2A", QColor(255, 0, 0)),
                                ParameterView("Công suất", "76W", QColor(0, 255, 0)),
                                ParameterView("Nhiệt độ", "45°C", QColor(0, 255, 0)),
                            ],
                        ),
                        ModuleView(
                            name="Module B",
                            parameters=[
                                ParameterView("Điện áp", "24.1V", QColor(0, 255, 0)),
                                ParameterView("Dòng", "3.2A", QColor(255, 0, 0)),
                                ParameterView("Công suất", "76W", QColor(0, 255, 0)),
                                ParameterView("Nhiệt độ", "45°C", QColor(0, 255, 0)),
                            ],
                        ),
                    ] )
            }
                
        def get_node(self, node_id):
            return self.nodes.get(node_id)
        
    
    app = QApplication(sys.argv)
    load_app_qss(app, ["ui/styles/dialog.qss", "ui/styles/info_view/module_style.qss", "ui/styles/info_view/parameter_style.qss", "ui/styles/system_diagram.qss"])
    tab = InfoTab(FakeSystemDataManager(), parent=None)
    tab.resize(1280, 1024)
    print(tab.styleSheet())
    tab.show()
    sys.exit(app.exec_())