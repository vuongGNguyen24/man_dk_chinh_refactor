from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QRect, QTimer, Qt
from typing import List, Callable, Dict
from .connection_effect import PathSegment


class ConnectionRender(QWidget):
    def __init__(self, connection_segments: Dict[str, List[PathSegment]], effects_function: Callable[[QPainter, List[PathSegment], bool], None]
, parent=None):
        super().__init__(parent)

        self.connection_segments = connection_segments
        self.connection_state: Dict[str, bool] = {}
        self.effects_function = effects_function

        # Overlay trong suốt
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def paintEvent(self, event):
        if not self.effects_function or not self.connection_segments:
            return

        #keep legacy logic
        if type(self.connection_segments) == list:
            self.connection_segments = {None: self.connection_segments}
        
        painter = QPainter(self)
        for key, segments in self.connection_segments.items():
            has_error = self.connection_state.get(key, False)
            self.effects_function(painter, segments, has_error)