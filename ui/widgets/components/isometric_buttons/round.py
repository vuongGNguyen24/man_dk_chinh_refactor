from PyQt5.QtGui import QPainter, QPen, QBrush, QColor, QRadialGradient
from PyQt5.QtCore import QRect, Qt
from .base import IsometricButton, IsometricVisualState

class IsometricRoundButton(IsometricButton):

    def _draw_shadow(self, painter, rect, pressed):
        if pressed:
            return
        state = self._visual_state
        painter.setBrush(QBrush(state.top_color.darker(150)))
        painter.setPen(QPen(state.border_color, 1))
        painter.drawEllipse(rect)

    def _draw_top_surface(self, painter, rect, pressed):
        state = self._visual_state
        color = state.top_color.darker(120) if pressed else state.top_color
        painter.setBrush(QBrush(color))
        painter.setPen(QPen(state.border_color, 1))
        painter.drawEllipse(rect)

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

    state = IsometricVisualState(
        top_color=QColor("#B43838"),
        border_color=QColor("#30ffffff"),
        text_color=QColor("#ffffff"),
        depth=6.0,
    )

    btn = IsometricRoundButton(state)
    btn.setText("OK")
    btn.setGeometry(100, 100, 100, 100)
    btn.show()

    sys.exit(app.exec_())
