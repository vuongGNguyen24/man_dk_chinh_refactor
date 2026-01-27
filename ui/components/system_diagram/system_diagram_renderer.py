from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QRect, QTimer, Qt
from typing import List
from diagram_layout_loader import DiagramLayoutLoader
from effects import EffectManager
from effects import PathSegment


class SystemDiagramRenderer(QWidget):
    """
    Widget render toàn bộ system diagram:
    - layout từ .ui
    - node + group box dùng style effect
    - connection dùng QPainter
    """

    def __init__(self, ui_file: str, system_data_manager, fps=40, parent=None):
        super().__init__(parent)
        

        # 1. Load layout
        self.loader = DiagramLayoutLoader(ui_file)
        self.root = self.loader.root
        self.root.setParent(self)

        # 2. Effect manager
        self.effects = EffectManager()

        # 3. Data source
        self.system_data_manager = system_data_manager

        # 4. Collect items
        self.nodes = self.loader.collect_nodes()
        self.group_boxes = self.loader.collect_group_boxes()
        self.connection_frames = self.loader.collect_connections()

        # 5. Build connection segments
        self.connection_segments = self._build_connection_segments()

        # 6. Apply static effects
        self._apply_group_box_effects()
        self._apply_node_effects()
        
        # 7. Start dynamic animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._on_tick)
        self.timer.start(int(1000 / fps))
        

        self.resize(self.root.size())
        
    def _on_tick(self):
        if self.effects.animation_enabled:
            self.update() #trigger paintEvent
        
    
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
    def _apply_node_effects(self):
        for name, widget in self.nodes.items():
            node = self.system_data_manager.get_node(name)
            has_error = node.has_error if node else False
            self.effects.apply_node_effect(widget, has_error=has_error)

    def _apply_group_box_effects(self):
        for _, group_box in self.group_boxes.items():
            self.effects.apply_group_box_effect(group_box)

    # ==================================================
    # CONNECTION BUILDING
    # ==================================================
    def _build_connection_segments(self):
        """
        Convert QFrame connection placeholders to PathSegment list
        """

        return self._map_connection_frames_to_segments() 

    def paintEvent(self, event):
        """Hàm được gọi kế thừa từ QWidget

        """
        super().paintEvent(event)
        painter = QPainter(self)
        self.effects.draw_connections(painter, self.connection_segments)

    # ==================================================
    # PUBLIC API
    # ==================================================
    def refresh_node_states(self):
        """
        Gọi khi data thay đổi (error / recover)
        """
        self._apply_node_effects()
        self.update()
        
if __name__ == "__main__":
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
        
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)
    data_manager = FakeSystemDataManager()
    renderer = SystemDiagramRenderer("sketech.ui", data_manager, fps=10)
    renderer.show()

    sys.exit(app.exec_())


    
