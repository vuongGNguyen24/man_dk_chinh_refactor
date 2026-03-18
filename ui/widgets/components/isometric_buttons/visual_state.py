from dataclasses import dataclass
from PyQt5.QtGui import QColor


@dataclass
class IsometricVisualState:
    top_color: QColor
    border_color: QColor
    text_color: QColor
    depth: float
    enabled: bool = True