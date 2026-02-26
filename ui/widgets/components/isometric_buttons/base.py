from dataclasses import dataclass

from .visual_state import IsometricVisualState
from PyQt5.QtCore import QRect, Qt
from PyQt5.QtGui import QColor, QPainter, QPen, QBrush, QFont, QRadialGradient
from PyQt5.QtWidgets import QPushButton
from ui.styles.isometric_button import IsometricTheme


    


class IsometricButton(QPushButton):

    def __init__(self, state: IsometricVisualState, parent=None):
        super().__init__(parent)

        self._visual_state: IsometricVisualState = state
        self._pressed = False

        # ---- isometric parameters ----
        self.squash_y = 0.75
        self.press_ratio = 0.5 
        self.shadow_strength = 0.8

        self.border_radius = 8


    
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
    # -------- hooks --------

    def on_pressed(self):
        pass

    def on_released(self):
        pass

    # -------- painting --------

    def paintEvent(self, event):
        if self._visual_state is None:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        state: IsometricVisualState = self._visual_state
        pressed = self._pressed

        w = self.width()
        h = self.height()

        # ---- geometry ----
        depth = state.depth
        z = depth * (self.press_ratio if pressed else 1.0)

        r = min(w, h) / 2
        ry = r * self.squash_y

        cx = w / 2
        cy = h / 2

        bottom_rect = QRect(
            int(cx - r),
            int(cy - ry),
            int(2 * r),
            int(2 * ry),
        )

        top_rect = QRect(
            int(cx - r),
            int(cy - ry - z),
            int(2 * r),
            int(2 * ry),
        )

        self._draw_shadow(painter, bottom_rect, z)
        self._draw_bottom_surface(painter, bottom_rect)
        self._draw_top_surface(painter, top_rect, pressed)
        self._draw_content(painter, top_rect)

    # ---- overridable parts ----

    def _draw_shadow(self, painter, rect, z):
        if z <= 0:
            return

        radius = rect.width() / 2
        shadow_offset = int(z * 0.6)
        shadow_opacity = int(60 * self.shadow_strength)

        shadow_rect = rect.translated(shadow_offset, shadow_offset)

        gradient = QRadialGradient(shadow_rect.center(), radius)
        gradient.setColorAt(0, QColor(0, 0, 0, shadow_opacity))
        gradient.setColorAt(1, QColor(0, 0, 0, 0))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(shadow_rect)


    def _draw_top_surface(self, painter, rect, pressed):
        state = self._visual_state
        color = state.top_color.darker(120) if pressed else state.top_color

        painter.setBrush(QBrush(color))
        painter.setPen(QPen(state.border_color, 1))
        painter.drawEllipse(rect)

    def _draw_content(self, painter, rect):
        state = self._visual_state

        if self.text():
            painter.setPen(QPen(state.text_color))
            painter.setFont(self.font())
            painter.drawText(rect, Qt.AlignCenter, self.text())

        icon = self.icon()
        if not icon.isNull():
            size = self.iconSize()
            icon_rect = QRect(
                rect.center().x() - size.width() // 2,
                rect.center().y() - size.height() // 2,
                size.width(),
                size.height(),
            )
            icon.paint(painter, icon_rect)

    def _draw_bottom_surface(self, painter, rect):
        state = self._visual_state

        radius = rect.width() / 2
        gradient = QRadialGradient(rect.center(), radius)

        base = state.top_color
        gradient.setColorAt(0, base.darker(150))
        gradient.setColorAt(1, base.darker(200))

        painter.setBrush(QBrush(gradient))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(rect)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QColor
    app = QApplication(sys.argv)
    button = IsometricButton(IsometricVisualState(QColor(255, 0, 0), QColor(0, 0, 255), QColor(0, 255, 0), 6), None)
    button.set_depth(2.5)
    button.pressed = True
    button.show()
    sys.exit(app.exec_())
    
