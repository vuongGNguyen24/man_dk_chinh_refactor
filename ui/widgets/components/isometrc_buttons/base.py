from dataclasses import dataclass

from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PyQt5.QtWidgets import QPushButton


@dataclass
class IsometricVisualState:
    top_color: QColor
    border_color: QColor
    text_color: QColor
    depth: float
    enabled: bool = True


class IsometricButton(QPushButton):

    def __init__(self, state: IsometricVisualState, parent=None):
        super().__init__(parent)

        self._visual_state: IsometricVisualState = state
        self._pressed = False

        self.offset_y = 6
        self.border_radius = 8
        self.top_surface_height = 80

    def apply_visual_state(self, state: IsometricVisualState):
        self._visual_state = state
        self.setEnabled(state.enabled)
        self.update()

    def set_depth(self, depth: float):
        if self._visual_state is None:
            return
        self._visual_state.depth = depth
        self.update()

        # -------- mouse handling --------

    def mousePressEvent(self, event):
        self._pressed = True
        self.on_pressed()
        self.update()
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        self._pressed = False
        self.on_released()
        self.update()
        super().mouseReleaseEvent(event)

    # -------- hooks (override nếu cần) --------

    def on_pressed(self):
        """Hook cho subclass hoặc controller"""
        pass

    def on_released(self):
        """Hook cho subclass hoặc controller"""
        pass
    
    def paintEvent(self, event):
        if self._visual_state is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        state = self._visual_state
        pressed = self._pressed

        w = self.width()
        h = self.top_surface_height
        depth = state.depth

        # ---- geometry ----
        top_y = depth if pressed else 0
        shadow_y = depth

        top_rect = QRect(0, top_y, w, h)
        shadow_rect = QRect(0, shadow_y, w, h)

        # ---- shadow (bottom) ----
        if not pressed:
            shadow_color = state.top_color.darker(150)
            painter.setBrush(QBrush(shadow_color))
            painter.setPen(QPen(state.border_color, 1))
            painter.drawRoundedRect(
                shadow_rect, self.border_radius, self.border_radius
            )

        # ---- top surface ----
        top_color = (
            state.top_color.darker(120) if pressed else state.top_color
        )

        painter.setBrush(QBrush(top_color))
        painter.setPen(QPen(state.border_color, 1))
        painter.drawRoundedRect(
            top_rect, self.border_radius, self.border_radius
        )

        # ---- text ----
        text = self.text()
        if text:
            painter.setPen(QPen(state.text_color))
            font = self.font()
            painter.setFont(font)
            painter.drawText(top_rect, Qt.AlignCenter, text)
        # ---- icon ----
        icon = self.icon()
        if not icon.isNull():
            size = self.iconSize()
            icon_rect = QRect(
                (w - size.width()) // 2,
                top_rect.y() + (h - size.height()) // 2,
                size.width(),
                size.height(),
            )
            icon.paint(painter, icon_rect)


    
