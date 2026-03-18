import math
from abc import ABC, abstractmethod
from typing import List, Dict
from dataclasses import dataclass
from PyQt5.QtCore import Qt, QRect, QTimer, QObject
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont, QFontMetrics, QLinearGradient
from PyQt5.QtWidgets import QWidget, QFrame

class GradientBuilder:
    def __init__(self, base_color: QColor):
        self.base_color = base_color

        self.normal = QColor(base_color)
        self.normal.setAlpha(60)

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
