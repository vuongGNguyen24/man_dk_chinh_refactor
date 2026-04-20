"""
Module for managing visual effects in the system diagram.
This module provides the EffectManager class which coordinates node states,
group box styling, and connection rendering.
"""

import time
from PyQt5.QtWidgets import QLabel, QGroupBox
from PyQt5.QtCore import Qt
from .connection import ConnectionEffect
from ....helpers.qss import repolish

class EffectManager:
    """
    Coordinates visual effects for the entire system diagram.

    It manages node state transitions (normal vs. error), group box styling,
    and delegating connection drawing to specialized effect handlers.

    Attributes:
        connection_effect: The handler for connection drawing logic.
        animation_enabled: Boolean flag to toggle animations.
        start_time: The timestamp when the manager was initialized.
    """

    def __init__(self):
        """
        Initializes the EffectManager.
        """
        self.connection_effect = ConnectionEffect()
        self.animation_enabled = True
        self.start_time = time.time()

    def elapsed_time(self) -> float:
        """
        Calculates the time elapsed since initialization.

        Returns:
            Seconds elapsed as a float.
        """
        return time.time() - self.start_time

    def apply_node_effect(self, widget: QLabel, *, has_error: bool):
        """
        Applies visual state to a node widget via QSS properties.

        Args:
            widget: The node QLabel to style.
            has_error: Whether the node is in an error state.
        """
        
        widget.setProperty("role", "node")
        widget.setProperty("state", "normal" if not has_error else "error")
        repolish(widget)
        
        #set center for text
        widget.setAlignment(Qt.AlignCenter)

    def apply_group_box_effect(self, group_box: QGroupBox):
        """
        Applies visual role to a group box widget.

        Args:
            group_box: The QGroupBox to style.
        """
        group_box.setProperty("role", "system")
        repolish(group_box)

    def draw_connections(self, painter, segments, has_error=False):
        """
        Draws animated or static connections between nodes.

        Args:
            painter: The QPainter instance to use for drawing.
            segments: List of PathSegment objects to draw.
            has_error: Whether the connection is in an error state.
        """
        self.connection_effect.draw(
            painter,
            segments,
            elapsed_time=self.elapsed_time(),
            animation_enabled=self.animation_enabled,
            has_error=has_error
        )

    def enable_animation(self, enabled: bool):
        """
        Enables or disables connection animations.

        Args:
            enabled: True to enable, False to disable.
        """
        self.animation_enabled = enabled

