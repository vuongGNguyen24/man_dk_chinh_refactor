"""
Module for the main system diagram view.
This module provides a widget that renders the entire system diagram, including
nodes, group boxes, and animated connections.
"""

from PyQt5.QtWidgets import QWidget, QFrame
from PyQt5.QtCore import QRect, QTimer, Qt, pyqtSignal
from typing import List, Union, Dict
import json

from ...helpers.svg_icon import svg_to_pixmap, load_svg_text, recolor_svg
from ...helpers.ui_widget_replacer import replace_ui_widget
from ...widgets.components.clickable_node_label import ClickableLabel
from .diagram_layout_loader import DiagramLayoutLoader
from .effects import EffectManager, PathSegment, ConnectionRender
from adapters.outbound.ui.node_status import QtSystemStatusAdapter
from application.dto import NodeStatus

class SystemDiagramView(QWidget):
    """
    Main widget for rendering the system diagram.

    It loads the layout from a .ui file, applies visual effects to nodes and group boxes,
    and renders animated connections using a custom QPainter overlay.

    Attributes:
        selected_node (pyqtSignal): Signal emitted when a node is clicked, carrying the node ID.
    """
    selected_node = pyqtSignal(str)
    
    def __init__(self, ui_file: str, svg_path: Union[str, None]=None, fps=40, init_error=True, parent=None, json_connections_path: Union[str, None]=None, node_adapter: Union[QtSystemStatusAdapter, None]=None):
        """
        Initializes the SystemDiagramView.

        Args:
            ui_file: Path to the .ui file for layout.
            svg_path: Path to the SVG icon file for ground indicators.
            fps: Frames per second for animations.
            init_error: Initial error state for connections.
            parent: Parent widget.
            json_connections_path: Path to the JSON mapping file for connections.
            node_adapter: Adapter for receiving node status updates.
        """
        super().__init__(parent)
        
        # 1. Load layout
        self.loader = DiagramLayoutLoader(ui_file)
        self.root = self.loader.root
        self.root.setParent(self)
        self._point_to_connections = self._load_mapping(json_connections_path) if json_connections_path else None
        self.connection_error_state: Dict[str, bool] = {}
                
        # 2. Effect manager
        self.effects = EffectManager()

        # 4. Collect items
        self.nodes = self.loader.collect_nodes()
        self.group_boxes = self.loader.collect_group_boxes()
        self.connection_frames = self.loader.collect_connections()
        
        # 5. Connect signals and init static effects
        if node_adapter:
            self.node_adapter = node_adapter
            self.node_adapter.node_status.connect(self._on_node_state_changed)
        self._connect_signals()
        self._init_static_effects()
        # 5. Build connection segments overlay
        self.connection_segments = self._build_connection_segments()
        self.overlay = ConnectionRender(self.connection_segments, self.effects.draw_connections, parent=self.root)
        if self._point_to_connections:
            for item in self._point_to_connections.keys():
                self.set_connection_state(item, init_error)
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
    
    def _load_mapping(self, path: str) -> Dict[str, List[str]]:
        """
        Loads connection mapping from a JSON file.

        Args:
            path: Path to the JSON file.

        Returns:
            Dictionary mapping connection point IDs to lists of item IDs.
        """
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _init_static_effects(self):
        """
        Initializes static visual effects for group boxes and nodes.
        """
        for object_name, group_box in self.group_boxes.items():
            self.effects.apply_group_box_effect(group_box)
        
        for object_name, node in self.nodes.items():
            self.effects.apply_node_effect(node, has_error=False)
    
    def _on_tick(self):
        """
        Timer callback for updating animations.
        """
        if self.effects.animation_enabled:
            self.overlay.update()

    
    
    def _connect_signals(self):
        """
        Converts QLabels to ClickableLabels and connects their clicked signals.
        """
        for object_name, label in self.nodes.items():
            label = ClickableLabel.from_qlabel(self.root, object_name, node_id=object_name)
            self.nodes[object_name] = label
            label.clicked.connect(self._on_node_clicked)

    def _on_node_clicked(self, node_id: str):
        """
        Handles node click events.

        Args:
            node_id: ID of the clicked node.
        """
        # print(node_id)
        self.selected_node.emit(node_id)
    
    def _insert_svg_icons(self):
        """
        Inserts SVG icons into ground indicator labels.
        """
        svg_string = load_svg_text(self.svg_path)
        svg_string = recolor_svg(svg_string, "#16b0d6")
        gnd_labels = self.loader.collect_gnd()
        for name, gnd_label in gnd_labels.items():
            icon = svg_to_pixmap(svg_string, gnd_label.size(), 255)
            gnd_label.setPixmap(icon)
    
    def _map_connection_frames_to_segments(self, connection_frames: Union[List[QFrame], None]=None) -> List[PathSegment]:
        """
        Maps QFrame rectangles to PathSegment objects for rendering.

        Args:
            connection_frames: List of QFrames to map. If None, uses all collected connection frames.

        Returns:
            List of PathSegment objects representing the connections.
        """
        from PyQt5.QtCore import QPoint
        
        segments = []
        if not connection_frames:
            connection_frames = self.connection_frames.values()
        for frame in connection_frames:
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
    
    def _build_connection_segments(self) -> Dict[str, List[PathSegment]]:
        """
        Converts QFrame placeholders and node connections to a mapping of segments.

        Returns:
            Dictionary mapping point IDs to lists of PathSegments.
        """
        if not self._point_to_connections:
            return {None: self._map_connection_frames_to_segments()}
            
        connection_segments_map = {}
        self.point_to_nodes_map = {}
        
        for point_id, item_ids in self._point_to_connections.items():
            conn_frames = []
            node_ids = []
            for item_id in item_ids:
                if item_id in self.connection_frames:
                    conn_frames.append(self.connection_frames[item_id])
                elif item_id in self.nodes:
                    node_ids.append(item_id)
                elif f"node_{item_id}" in self.nodes:
                    node_ids.append(f"node_{item_id}")
                    
            connection_segments_map[point_id] = self._map_connection_frames_to_segments(conn_frames)
            self.point_to_nodes_map[point_id] = node_ids
            
        return connection_segments_map
    
    def _on_node_state_changed(self, node_state: NodeStatus):
        """
        Handles node state change updates.

        Args:
            node_state: The new status of the node.
        """
        node_id = node_state.node_id
        has_error = node_state.has_error
        node = self.nodes.get(f"node_{node_id}")
        self.effects.apply_node_effect(node, has_error)
    
    def set_connection_state(self, point_id: str, has_error: bool):
        """
        Sets the visual state of a connection and its associated nodes.

        Args:
            point_id: ID of the connection point.
            has_error: True if the connection is in an error state.
        """
        self.overlay.connection_state[point_id] = has_error
        
        # Cập nhật style cho các nodes đi kèm với connection này (nếu có)
        if hasattr(self, 'point_to_nodes_map') and point_id in self.point_to_nodes_map:
            for node_id in self.point_to_nodes_map[point_id]:
                node = self.nodes.get(node_id)
                if node:
                    state_str = "electric_disconnected" if has_error else "electric_connected"
                    node.setProperty("state", state_str)
                    node.style().unpolish(node)
                    node.style().polish(node)
                    node.update()
        
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from ...helpers.qss import load_app_qss
    app = QApplication(sys.argv)
    load_app_qss(app, ["ui/styles/system_diagram.qss"])
    
    renderer = SystemDiagramView("ui/views/system_diagram/layout/system_diagram.ui", fps=30, json_connections_path="ui/views/system_diagram/layout/system_connection_mapping.json")
    renderer.show()

    sys.exit(app.exec_())



    
