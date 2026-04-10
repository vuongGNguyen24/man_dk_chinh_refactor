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
    x1: float
    y1: float
    x2: float
    y2: float


class WaveCalculator:
    def __init__(
        self,
        wave_length=60,
        wave_spacing=120,
        cycle_time=2.5,
    ):
        self.wave_length = wave_length
        self.wave_spacing = wave_spacing
        self.cycle_time = cycle_time

    def compute_wave_positions(self, total_length: float, elapsed_time: float) -> List[float]:
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
    def draw_segment(
        self,
        painter: QPainter,
        segment: PathSegment,
        gradient_stops: Dict,
        fallback_color: QColor,
        width=3,
    ):
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

#error_color = QColor(238, 44, 44)
class ConnectionEffect:
    def __init__(self, base_color=QColor(255, 0, 0), error_color=QColor(100, 200, 255, 40)):
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
