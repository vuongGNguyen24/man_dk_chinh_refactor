from typing import Union
from PyQt5.QtWidgets import QWidget, QHBoxLayout
from PyQt5.QtCore import Qt

from ui.views.effects.grid_background_renderer import GridBackgroundWidget
from ui.views.system_diagram.system_diagram_view import SystemDiagramView
from ui.views.info_view.info_panel_renderer import InfoPanelRenderer
from ui.widgets.components.status_indicator_widget import StatusIndicatorWidget
from adapters.outbound.ui.node_status import QtSystemStatusAdapter
from ui.helpers.qss import set_multiple_property

class FiringCircultTab(GridBackgroundWidget):
    """
    Coordinator cho tab Hệ thống (refactored)
    """

    def __init__(self,  node_adapter: Union[QtSystemStatusAdapter, None] = None, parent=None):
        super().__init__(
            parent,
            enable_animation=True,
        )

        set_multiple_property(self, role='background')
        # ===== Layout =====
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # ===== System diagram =====
        self.diagram = SystemDiagramView(
            ui_file="ui/views/system_diagram/layout/dk_tai_cho.ui",
            fps=30,
            node_adapter=node_adapter,
            json_connections_path="ui/views/system_diagram/layout/dk_tai_cho_connection_mapping.json",
            svg_path="ui/resources/Icons/gnd.svg",
        )
        layout.addWidget(self.diagram, stretch=3)

        



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from dataclasses import dataclass
    from PyQt5.QtGui import QColor
    from typing import List
    from ui.helpers.qss import load_styles_from_yaml
        
    
    app = QApplication(sys.argv)
    load_styles_from_yaml(app, "style_manifest.yaml", base_path="ui/styles")
    tab = FiringCircultTab(parent=None)
    tab.resize(1280, 1024)
    print(tab.styleSheet())
    tab.show()
    sys.exit(app.exec_())