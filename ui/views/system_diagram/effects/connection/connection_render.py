from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QRect, QTimer, Qt
from typing import List, Callable
from diagram_layout_loader import DiagramLayoutLoader
from .connection_effect import PathSegment


class ConnectionRender(QWidget):
    def __init__(self, connection_segments: List[PathSegment], effects_function: Callable[[QPainter, List[PathSegment]], None]
, parent=None):
        super().__init__(parent)

        self.connection_segments = connection_segments
        self.effects_function = effects_function

        # Overlay trong suốt
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        if not self.effects_function or not self.connection_segments:
            return

        painter = QPainter(self)
        self.effects_function(painter, self.connection_segments)