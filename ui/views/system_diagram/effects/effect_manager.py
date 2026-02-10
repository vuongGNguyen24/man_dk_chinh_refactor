import time
from PyQt5.QtWidgets import QLabel, QGroupBox
from PyQt5.QtCore import Qt
from .connection import ConnectionEffect
from ....helpers.qss import repolish

class EffectManager:
    """
    Điều phối effect cho toàn bộ system diagram
    """

    def __init__(self):
        self.connection_effect = ConnectionEffect()
        self.animation_enabled = True
        self.start_time = time.time()

    def elapsed_time(self) -> float:
        return time.time() - self.start_time

    def apply_node_effect(self, widget: QLabel, *, has_error: bool):
        """
        Apply node visual state via style effect 
        """
        widget.setProperty("role", "node")
        widget.setProperty("state", "normal" if not has_error else "error")
        repolish(widget)

    def apply_group_box_effect(self, group_box: QGroupBox):
        """
        Apply group box visual role
        """
        group_box.setProperty("role", "system")
        repolish(group_box)

    def draw_connections(self, painter, segments, has_error=False):
        """
        Draw animated/static connections
        """
        self.connection_effect.draw(
            painter,
            segments,
            elapsed_time=self.elapsed_time(),
            animation_enabled=self.animation_enabled,
            has_error=has_error
        )

    def enable_animation(self, enabled: bool):
        self.animation_enabled = enabled
