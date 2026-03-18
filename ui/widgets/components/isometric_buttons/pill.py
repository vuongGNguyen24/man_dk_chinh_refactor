from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QRadialGradient
from PyQt5.QtCore import Qt
from .base import IsometricButton, IsometricVisualState


class IsometricPillButton(IsometricButton):

    def _draw_shadow(self, painter, rect, pressed):
        if pressed:
            return
        r = self.border_radius
        state = self._visual_state
        painter.setBrush(QBrush(state.top_color.darker(150)))
        painter.setPen(QPen(state.border_color, 1))
        painter.drawRoundedRect(rect, r, r)

    def _draw_top_surface(self, painter, rect, pressed):
        r = self.border_radius
        state = self._visual_state
        color = state.top_color.darker(120) if pressed else state.top_color
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(state.border_color, 1))
        painter.drawRoundedRect(rect, r, r)
        
        
    def _draw_bottom_surface(self, painter, rect):
        state = self._visual_state
        r = self.border_radius
        radius = rect.width() / 2
        gradient = QRadialGradient(rect.center(), radius)

        base = state.top_color
        gradient.setColorAt(0, base.darker(150))
        gradient.setColorAt(1, base.darker(200))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(rect, r, r)
