"""
Module for connection visual effects.
This module provides classes for calculating wave animations and painting
connections with gradients and animated effects.
"""

import math
from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass
from PyQt5.QtCore import Qt, QRect, QTimer, QObject
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont, QFontMetrics, QLinearGradient
from PyQt5.QtWidgets import QWidget, QFrame

from .gradient_builder import GradientBuilder


@dataclass
class PathSegment:
    """
    Represents a line segment in a connection path.

    Attributes:
        x1: Start X coordinate.
        y1: Start Y coordinate.
        x2: End X coordinate.
        y2: End Y coordinate.
    """
    x1: float
    y1: float
    x2: float
    y2: float


class WaveCalculator:
    """
    Calculates the positions of animated waves moving along a path.

    Attributes:
        wave_length: The length of a single wave.
        wave_spacing: The distance between consecutive waves.
        cycle_time: The time in seconds for a wave to complete a cycle.
    """
    def __init__(
        self,
        wave_length=60,
        wave_spacing=120,
        cycle_time=2.5,
    ):
        """
        Initializes the WaveCalculator.
        """
        self.wave_length = wave_length
        self.wave_spacing = wave_spacing
        self.cycle_time = cycle_time

    def compute_wave_positions(self, total_length: float, elapsed_time: float) -> List[float]:
        """
        Computes the current positions of all waves on a path of given length.

        Args:
            total_length: Total length of the connection path.
            elapsed_time: Time elapsed since animation start.

        Returns:
            List of float positions representing the center of each wave.
        """
        wave_half = self.wave_length / 2
        cycle_progress = (elapsed_time % self.cycle_time) / self.cycle_time

        num_waves = max(2, int(total_length / self.wave_spacing) + 2)

        positions = []
        for i in range(num_waves):
            offset = i * self.wave_spacing
            base = total_length + wave_half - cycle_progress * (total_length + self.wave_length)
            positions.append(base - offset)

        return positions
    

class ConnectionPainter:
    """
    Handles the low-level painting of connection segments.
    """
    def draw_segment(
        self,
        painter: QPainter,
        segment: PathSegment,
        gradient_stops: Dict[float, QColor],
        fallback_color: QColor,
        width=3,
    ):
        """
        Draws a single path segment with an optional gradient.

        Args:
            painter: The QPainter instance.
            segment: The PathSegment to draw.
            gradient_stops: Dictionary of gradient stops (position: color).
            fallback_color: Color to use if no gradient is provided.
            width: Line width.
        """
        if not gradient_stops:
            pen = QPen(fallback_color, width)
            painter.setPen(pen)
            painter.drawLine(segment.x1, segment.y1, segment.x2, segment.y2)
            return

        gradient = QLinearGradient(
            segment.x1, segment.y1,
            segment.x2, segment.y2
        )
        for pos, color in gradient_stops.items():
            gradient.setColorAt(pos, color)

        pen = QPen(QBrush(gradient), width)
        painter.setPen(pen)
        painter.drawLine(segment.x1, segment.y1, segment.x2, segment.y2)


class ConnectionEffect:
    """
    High-level class for rendering animated connections.

    Attributes:
        base_color: The default color for connections.
        error_color: The color used when a connection has an error.
        wave_calc: Specialized calculator for wave positions.
        painter: Specialized painter for line segments.
        gradient_builder: Specialized builder for gradient stops.
    """
    def __init__(self, base_color=QColor(255, 0, 0), error_color=QColor(100, 200, 255, 40)):
        """
        Initializes the ConnectionEffect.
        """
        self.base_color = base_color
        self.error_color = error_color
        self.wave_calc = WaveCalculator()
        self.painter = ConnectionPainter()
        self.gradient_builder = GradientBuilder(self.base_color)
        self.wave_length = 60

    def draw(
        self,
        painter: QPainter,
        segments: List[PathSegment],
        elapsed_time: float,
        has_error: bool,
        animation_enabled: bool,
    ):
        """
        Draws a set of connected segments with optional animation and error states.

        Args:
            painter: The QPainter instance.
            segments: List of PathSegment objects to draw.
            elapsed_time: Current animation timestamp.
            has_error: Whether the connection is in an error state.
            animation_enabled: Whether to enable wave animations.
        """
        if not animation_enabled:
            self.painter.draw_segment(painter, segments, None, self.base_color)
            return
        
        total_length = sum(
            math.hypot(s.x2 - s.x1, s.y2 - s.y1)
            for s in segments
        )
        if total_length == 0:
            return

        waves = self.wave_calc.compute_wave_positions(total_length, elapsed_time)

        normal = QColor(self.base_color)
        normal.setAlpha(100)

        cursor = 0.0
        for s in segments:
            if has_error:
                self.painter.draw_segment(painter, s, None, self.error_color)
                continue
            seg_len = math.hypot(s.x2 - s.x1, s.y2 - s.y1)
            if seg_len == 0:
                continue

            stops = self.gradient_builder.build(
                cursor,
                seg_len,
                total_length,
                waves,
                self.wave_length,
            )

            # QUAN TRỌNG: luôn có baseline
            if stops:
                stops[0.0] = normal
                stops[1.0] = normal

            self.painter.draw_segment(
                painter,
                s,
                stops,
                normal,
            )

            cursor += seg_len

