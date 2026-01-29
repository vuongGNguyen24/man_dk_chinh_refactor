import time
from PyQt5.QtWidgets import QWidget, QGroupBox

from .connection import ConnectionEffect
from .style_effect import NodeStyleEffect, GroupBoxStyleEffect


class EffectManager:
    """
    Điều phối effect cho toàn bộ system diagram
    """

    def __init__(self):
        self.node_style = NodeStyleEffect()
        self.group_box_style = GroupBoxStyleEffect()

        self.connection_effect = ConnectionEffect()

        self.animation_enabled = True
        self.start_time = time.time()

    def elapsed_time(self) -> float:
        return time.time() - self.start_time

    def apply_node_effect(self, widget: QWidget, *, has_error: bool):
        """
        Apply style to node widget
        """
        style = self.node_style.style(has_error=has_error)
        widget.setStyleSheet(style)

    def apply_group_box_effect(self, group_box: QGroupBox):
        """
        Apply style to group box
        """
        style = self.group_box_style.style()
        group_box.setStyleSheet(style)

    def draw_connections(self, painter, segments):
        """
        Draw animated/static connections
        """
        self.connection_effect.draw(
            painter,
            segments,
            elapsed_time=self.elapsed_time(),
            animation_enabled=self.animation_enabled
        )

    def enable_animation(self, enabled: bool):
        self.animation_enabled = enabled
