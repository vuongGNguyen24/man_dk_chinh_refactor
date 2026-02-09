from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QRect, QTimer, Qt, pyqtSignal
from typing import List, Union

from ...helpers.svg_icon import svg_to_pixmap, load_svg_text, recolor_svg
from ...helpers.ui_widget_replacer import replace_ui_widget
from ...widgets.components.clickable_node_label import ClickableLabel
from .diagram_layout_loader import DiagramLayoutLoader
from .effects import EffectManager, PathSegment, ConnectionRender


class SystemDiagramView(QWidget):
    """
    Widget render toàn bộ system diagram:
    - layout từ .ui
    - node + group box dùng style effect
    - connection dùng QPainter
    """
    selected_node = pyqtSignal(str)
    
    def __init__(self, ui_file: str, system_data_manager, svg_path: Union[str, None]=None, fps=40, parent=None):
        super().__init__(parent)
        
        # 1. Load layout
        self.loader = DiagramLayoutLoader(ui_file)
        self.root = self.loader.root
        print(self.root.styleSheet())
        self.root.setParent(self)
        
        # 2. Effect manager
        self.effects = EffectManager()

        # 3. Data source
        self.system_data_manager = system_data_manager

        # 4. Collect items
        #TODO: add click event to node labels
        self.nodes = self.loader.collect_nodes()
        self.group_boxes = self.loader.collect_group_boxes()
        self.connection_frames = self.loader.collect_connections()
        self._connect_signals()
        self._init_static_effects()
        # 5. Build connection segments overlay
        self.connection_segments = self._build_connection_segments()
        self.overlay = ConnectionRender(self.connection_segments, self.effects.draw_connections, parent=self.root)
        self.overlay.resize(self.root.size())
        self.overlay.raise_()   # ⬅️ đảm bảo nằm trên cùng
        
        if svg_path:
            self.svg_path = svg_path
            self._insert_svg_icons()
        # 7. Start dynamic animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(int(1000 / fps))
        

        self.resize(self.root.size())
    
    def _init_static_effects(self):
        for object_name, group_box in self.group_boxes.items():
            self.effects.apply_group_box_effect(group_box)
        
        for object_name, node in self.nodes.items():
            self.effects.apply_node_effect(node, has_error=False)
    
    def _on_tick(self):
        if self.effects.animation_enabled:
            self.overlay.update()

    
    
    def _connect_signals(self):
        for object_name, label in self.nodes.items():
            label = ClickableLabel.from_qlabel(self.root, object_name, node_id=object_name)
            self.nodes[object_name] = label
            label.clicked.connect(self._on_node_clicked)

    def _on_node_clicked(self, node_id: str):
        # print(node_id)
        self.selected_node.emit(node_id)
    
    def _insert_svg_icons(self):
        """
        Insert icon to node
        """
        svg_string = load_svg_text(self.svg_path)
        svg_string = recolor_svg(svg_string, "#16b0d6")
        gnd_labels = self.loader.collect_gnd()
        for name, gnd_label in gnd_labels.items():
            print(name)
            
            icon = svg_to_pixmap(svg_string, gnd_label.size(), 255)
            gnd_label.setPixmap(icon)
    
    def _map_connection_frames_to_segments(self) -> List[PathSegment]:
        from PyQt5.QtCore import QPoint

        segments = []

        for _, frame in self.connection_frames.items():
            rect = frame.rect()

            start, end = None, None
            is_horizontal = rect.width() >= rect.height()
            if is_horizontal:
                start = QPoint(rect.left(), rect.center().y())
                end   = QPoint(rect.right(), rect.center().y())
            else:
                #vertical line 
                start = QPoint(rect.center().x(), rect.top())
                end   = QPoint(rect.center().x(), rect.bottom())

            p1 = frame.mapTo(self, start)
            p2 = frame.mapTo(self, end)


            segments.append(
                PathSegment(p1.x(), p1.y(), p2.x(), p2.y())
            )

            frame.hide()

        return segments
    

    def _build_connection_segments(self):
        """
        Convert QFrame connection placeholders to PathSegment list
        """

        return self._map_connection_frames_to_segments() 

    def refresh_node_states(self):
        """
        Gọi khi data thay đổi (error / recover)
        """
        for node_id, node in self.nodes.items():
            pass
        
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from ...helpers.qss import load_app_qss
    class FakeNode:
        def __init__(self, has_error=False):
            self.has_error = has_error


    class FakeSystemDataManager:
        def __init__(self):
            self.nodes = {
                "node_1": FakeNode(False),
                "node_2": FakeNode(True),
            }

        def get_node(self, node_id):
            return self.nodes.get(node_id)
        
    
    app = QApplication(sys.argv)
    load_app_qss(app, ["ui/styles/system_diagram.qss"])
    # print(app.styleSheet())
    data_manager = FakeSystemDataManager()
    
    renderer = SystemDiagramView("ui/views/system_diagram/layout/system_diagram.ui", data_manager, fps=20)
    renderer.show()

    sys.exit(app.exec_())


    
