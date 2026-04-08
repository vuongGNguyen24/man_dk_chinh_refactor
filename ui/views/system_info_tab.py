from typing import Union
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

from ui.views.effects.grid_background_renderer import GridBackgroundWidget
from ui.views.system_diagram.system_diagram_view import SystemDiagramView
from ui.views.info_view.info_panel_renderer import InfoPanelRenderer
from ui.widgets.components.status_indicator_widget import StatusIndicatorWidget
from adapters.outbound.ui.node_status import QtSystemStatusAdapter
from ui.helpers.qss import set_multiple_property

class InfoTab(GridBackgroundWidget):
    """
    Coordinator cho tab Hệ thống (refactored)
    """

    def __init__(self,  node_adapter: Union[QtSystemStatusAdapter, None] = None, parent=None):
        super().__init__(
            parent,
            enable_animation=True,
        )


        # ===== Layout =====
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        # ===== System diagram =====
        self.diagram = SystemDiagramView(
            ui_file="ui/views/system_diagram/layout/system_diagram.ui",
            fps=30,
            node_adapter=node_adapter,
            json_connections_path="ui/views/system_diagram/layout/system_connection_mapping.json",
        )
        layout.addWidget(self.diagram, stretch=3)

        # ===== Info panel =====
        self.info_panel = InfoPanelRenderer(
            
            "ui/views/info_view/infor_panel_reader.ui"
        )
        self.info_panel.hide()
        layout.addWidget(self.info_panel, stretch=2)
        self.node_adapter = node_adapter
        self.status_indicator = StatusIndicatorWidget(self)
        self.status_indicator.show()

        self.shut_down_button = QtWidgets.QPushButton("Tắt máy", parent=self)
        self.shut_down_button.clicked.connect(self.on_shut_down_clicked)
        self.shut_down_button.setFixedHeight(35)
        self.shut_down_button.setFixedWidth(100)
        set_multiple_property(self.shut_down_button, role="primary", variant="cancel")
        self.shut_down_button.show()
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
        self.shut_down_button.setGeometry(
            self.width() - self.shut_down_button.width() - margin,
            self.height() - self.shut_down_button.height() - margin,
            self.shut_down_button.width(),
            self.shut_down_button.height()
        )

    # --------------------------------------------------
    # Slots
    # --------------------------------------------------
    def _on_node_selected(self, node_id: str):
        """
        Khi user click vào node trong sơ đồ
        """
        # print(node_id)
        node_data = self.node_adapter.get_node(node_id) if self.node_adapter else None
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

    def on_shut_down_clicked(self):
        """Tắt máy
        """
        import os
        os.system("shutdown now")

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from dataclasses import dataclass
    from PyQt5.QtGui import QColor
    from typing import List
    from ui.helpers.qss import load_app_qss
        
    
    app = QApplication(sys.argv)
    load_app_qss(app, ["ui/styles/dialog.qss", "ui/styles/info_view/module_style.qss", "ui/styles/info_view/parameter_style.qss", "ui/styles/system_diagram.qss"])
    tab = InfoTab(parent=None)
    tab.resize(1280, 1024)
    print(tab.styleSheet())
    tab.show()
    sys.exit(app.exec_())