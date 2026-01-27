from abc import ABC, abstractmethod

from PyQt5.QtCore import Qt, QRect, QTimer, QObject
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont, QFontMetrics, QLinearGradient
from PyQt5.QtWidgets import QWidget, QFrame


class StyleEffect(ABC):
    @abstractmethod
    def style(self, state: dict) -> str:
        pass
    
class NodeStyleEffect(StyleEffect):
    def style(self, *, has_error: bool) -> str:
        if has_error:
            return """
            QLabel {
                background-color: rgb(255, 0, 0);
                color: white;
                border: 1px solid rgb(100, 200, 255);
            }
            """
        return """
        QLabel {
            background-color: white;
            color: black;
            border: 1px solid rgb(100, 200, 255);
        }
        """

class GroupBoxStyleEffect(StyleEffect):
    def style(self) -> str:
        return """
        QGroupBox {
            border: 2px dashed rgb(255, 255, 255);
            background-color: black;
            margin-top: 10px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: bottom left;
            padding: 0 5px;
            color: white;
        }
        """

