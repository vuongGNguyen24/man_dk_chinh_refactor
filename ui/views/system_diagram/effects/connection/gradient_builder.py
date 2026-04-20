"""
Module for building linear gradients for animated connections.
This module provides the GradientBuilder class which calculates color stops
to create a moving wave effect on line segments.
"""

import math
from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass
from PyQt5.QtCore import Qt, QRect, QTimer, QObject
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont, QFontMetrics, QLinearGradient
from PyQt5.QtWidgets import QWidget, QFrame

class GradientBuilder:
    """
    Builder for calculating gradient stops for connection animations.

    It creates a list of color stops for a QLinearGradient to simulate a bright
    pulse or wave moving along a path.

    Attributes:
        base_color: The reference color used for the gradient.
        normal: The base color with low alpha for the background line.
        medium: The base color with medium alpha for the wave edges.
        bright: A brightened version of the base color for the wave center.
    """
    def __init__(self, base_color: QColor):
        """
        Initializes the GradientBuilder with a base color.

        Args:
            base_color: The QColor to use as the foundation for the gradient.
        """
        self.base_color = base_color

        self.normal = QColor(base_color)
        self.normal.setAlpha(100)

        self.medium = QColor(base_color)
        self.medium.setAlpha(180)

        self.bright = QColor(
            min(255, base_color.red() + 50),
            min(255, base_color.green() + 50),
            min(255, base_color.blue() + 50),
        )
        self.bright.setAlpha(255)

    def build(
        self,
        seg_start: float,
        seg_length: float,
        total_length: float,
        wave_positions: List[float],
        wave_length: float,
    ) -> Dict[float, QColor]:
        """
        Builds a dictionary of gradient stops for a specific path segment.

        Args:
            seg_start: The starting distance of this segment along the total path.
            seg_length: The length of this specific segment.
            total_length: The total length of the entire connection path.
            wave_positions: List of wave center positions along the path.
            wave_length: The total width of a single wave.

        Returns:
            A dictionary mapping stop positions (0.0 to 1.0) to QColor objects.
        """
        stops = {}
        half = wave_length / 2

        for wave_pos in wave_positions:
            wave_start = wave_pos - half
            wave_end = wave_pos + half

            # giống effect cũ
            if wave_end < seg_start or wave_start > seg_start + seg_length:
                continue
            if not (0 <= wave_pos <= total_length):
                continue

            center = (wave_pos - seg_start) / seg_length
            center = max(0.0, min(1.0, center))

            spread = 0.06
            for pos, color in [
                (center - spread, self.medium),
                (center, self.bright),
                (center + spread, self.medium),
            ]:
                if 0 <= pos <= 1:
                    key = round(pos * 1000)
                    if key not in stops or stops[key].alpha() < color.alpha():
                        stops[key] = color

        return {k / 1000.0: v for k, v in stops.items()}

