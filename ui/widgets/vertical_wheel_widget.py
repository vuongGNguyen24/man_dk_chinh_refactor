# -*- coding: utf-8 -*-

import math, os, sys
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer, pyqtProperty, QPropertyAnimation, QEasingCurve


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class VerticalWheelWidget(QWidget):
    def __init__(self, current_angle, aim_angle, parent=None):
        super().__init__(parent)
        self._current_angle = current_angle
        self._aim_angle = aim_angle
        self.static_pixmap = None
        self._current_angle_anim = QPropertyAnimation(self, b"currentAngle")
        self._aim_angle_anim = QPropertyAnimation(self, b"aimAngle")
        self._current_angle_anim.setDuration(500)
        self._aim_angle_anim.setDuration(500)
        self._current_angle_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._aim_angle_anim.setEasingCurve(QEasingCurve.InOutQuad)

    def getCurrentAngle(self):
        return self._current_angle
    def setCurrentAngle(self, value):
        self._current_angle = value
        self.update()
    currentAngle = pyqtProperty(float, fget=getCurrentAngle, fset=setCurrentAngle)

    def getAimAngle(self):
        return self._aim_angle
    def setAimAngle(self, value):
        self._aim_angle = value
        self.update()
    aimAngle = pyqtProperty(float, fget=getAimAngle, fset=setAimAngle)

    def resizeEvent(self, event):
        # Only create static pixmap when widget has a valid size
        w = max(0, self.width())
        h = max(0, self.height())
        if w <= 0 or h <= 0:
            self.static_pixmap = None
            return

        self.static_pixmap = QPixmap(w, h)
        self.static_pixmap.fill(Qt.transparent)
        painter = QPainter()
        if not painter.begin(self.static_pixmap):
            self.static_pixmap = None
            return
        painter.setRenderHint(QPainter.Antialiasing)
        total_width = self.width()
        total_height = self.height()
        wheel_width = 100
        wheel_height = min(total_height * 0.75, 220)
        spacing = 40
        total_needed_width = 2 * wheel_width + spacing
        start_x = (total_width - total_needed_width) / 2
        center_y = total_height / 2
        left_center = QPointF(start_x + wheel_width/2, center_y)
        right_center = QPointF(start_x + wheel_width + spacing + wheel_width/2, center_y)
        self._draw_vertical_wheel_static(painter, left_center, wheel_width, wheel_height, is_left=True)
        self._draw_vertical_wheel_static(painter, right_center, wheel_width, wheel_height, is_left=False)
        if painter.isActive():
            painter.end()

    def update_angle(self, current_angle: float = 0, aim_angle: float = 0) -> None:
        if self._current_angle != current_angle:
            self._current_angle_anim.stop()
            self._current_angle_anim.setStartValue(self._current_angle)
            self._current_angle_anim.setEndValue(current_angle)
            self._current_angle_anim.start()
        else:
            self.setCurrentAngle(current_angle)
        if self._aim_angle != aim_angle:
            self._aim_angle_anim.stop()
            self._aim_angle_anim.setStartValue(self._aim_angle)
            self._aim_angle_anim.setEndValue(aim_angle)
            self._aim_angle_anim.start()
        else:
            self.setAimAngle(aim_angle)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.static_pixmap:
            painter.drawPixmap(0, 0, self.static_pixmap)
        total_width = self.width()
        total_height = self.height()
        wheel_width = 100
        wheel_height = min(total_height * 0.75, 220)
        spacing = 40
        total_needed_width = 2 * wheel_width + spacing
        start_x = (total_width - total_needed_width) / 2
        center_y = total_height / 2
        left_center = QPointF(start_x + wheel_width/2, center_y)
        right_center = QPointF(start_x + wheel_width + spacing + wheel_width/2, center_y)
        self._draw_vertical_wheel_dynamic(painter, left_center, wheel_width, wheel_height, self._current_angle, is_left=True)
        self._draw_vertical_wheel_dynamic(painter, right_center, wheel_width, wheel_height, self._aim_angle, is_left=False)

    def _draw_vertical_wheel_static(self, painter: QPainter, center: QPointF, width: float, height: float, is_left: bool = True) -> None:
        # ...existing code...
        wheel_rect = QRectF(center.x() - width/2, center.y() - height/2, width, height)
        painter.setPen(QPen(QColor(150, 150, 150), 2))
        painter.setBrush(QColor(80, 80, 80, 100))
        painter.drawRoundedRect(wheel_rect, 10, 10)
        highlight_rect = QRectF(center.x() - width/2 + 5, center.y() - 10, width - 10, 20)
        from PyQt5.QtGui import QLinearGradient, QRadialGradient
        glass_gradient = QLinearGradient(highlight_rect.topLeft(), highlight_rect.bottomRight())
        glass_gradient.setColorAt(0, QColor(255, 255, 255, 30))
        glass_gradient.setColorAt(0.5, QColor(255, 255, 255, 15))
        glass_gradient.setColorAt(1, QColor(255, 255, 255, 40))
        painter.setPen(Qt.NoPen)
        painter.setBrush(glass_gradient)
        painter.drawRoundedRect(highlight_rect, 8, 8)
        glass_border = QPen(QColor(255, 255, 255, 80), 1)
        painter.setPen(glass_border)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(highlight_rect, 8, 8)
        shine_rect = QRectF(highlight_rect.x() + 2, highlight_rect.y() + 2, highlight_rect.width() - 4, highlight_rect.height() * 0.4)
        shine_gradient = QLinearGradient(shine_rect.topLeft(), shine_rect.bottomLeft())
        shine_gradient.setColorAt(0, QColor(255, 255, 255, 60))
        shine_gradient.setColorAt(1, QColor(255, 255, 255, 0))
        painter.setPen(Qt.NoPen)
        painter.setBrush(shine_gradient)
        painter.drawRoundedRect(shine_rect, 6, 6)
        indicator_x = center.x() + (width/2 + 15) if is_left else center.x() - (width/2 + 15)
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(QColor(255, 255, 255))
        triangle_size = 8
        if is_left:
            painter.drawPolygon([
                QPointF(indicator_x, center.y()),
                QPointF(indicator_x - triangle_size, center.y() - triangle_size/2),
                QPointF(indicator_x - triangle_size, center.y() + triangle_size/2)
            ])
        else:
            painter.drawPolygon([
                QPointF(indicator_x, center.y()),
                QPointF(indicator_x + triangle_size, center.y() - triangle_size/2),
                QPointF(indicator_x + triangle_size, center.y() + triangle_size/2)
            ])

    def _draw_vertical_wheel_dynamic(self, painter: QPainter, center: QPointF, width: float, height: float, angle: float, is_left: bool = True) -> None:
        # ...existing code...
        angle_range = 60
        wheel_range = height * 0.7
        normalized_angle = max(0, min(angle_range, angle)) / angle_range
        wheel_offset = -((normalized_angle - 0.5) * wheel_range)
        self._draw_vertical_marks_with_offset(painter, center, width, height, wheel_offset, is_left)
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.setPen(QPen(Qt.white, 2))
        if is_left:
            line1 = "GÓC TẦM"
            line2 = "HIỆN TẠI"
        else:
            line1 = "GÓC TẦM"
            line2 = "MỤC TIÊU"
        label_rect1 = QRectF(center.x() - width/2, center.y() - height/2 - 40, width, 15)
        painter.drawText(label_rect1, Qt.AlignCenter, line1)
        label_rect2 = QRectF(center.x() - width/2, center.y() - height/2 - 25, width, 15)
        painter.drawText(label_rect2, Qt.AlignCenter, line2)
        value_rect = QRectF(center.x() - width/2, center.y() + height/2 + 5, width, 20)
        painter.drawText(value_rect, Qt.AlignCenter, f"{angle:.1f}°")

    def _draw_vertical_marks_with_offset(self, painter: QPainter, center: QPointF, width: float, height: float, offset_y: float, is_left: bool = True) -> None:
        # ...existing code...
        painter.setPen(QPen(Qt.white, 1))
        for angle in range(0, 61, 5):
            normalized_angle = (60 - angle) / 60.0
            y_pos = center.y() - height/2 * 0.7 + normalized_angle * height * 0.7 + offset_y
            if center.y() - height/2 + 10 <= y_pos <= center.y() + height/2 - 10:
                if angle % 15 == 0:
                    mark_width = width * 0.3
                    painter.setPen(QPen(Qt.white, 2))
                elif angle % 10 == 0:
                    mark_width = width * 0.2
                    painter.setPen(QPen(Qt.white, 1.5))
                else:
                    mark_width = width * 0.1
                    painter.setPen(QPen(Qt.white, 1))
                start_x = center.x() - mark_width/2
                end_x = center.x() + mark_width/2
                painter.drawLine(QPointF(start_x, y_pos), QPointF(end_x, y_pos))
                if angle % 15 == 0:
                    font = painter.font()
                    font.setPointSize(8)
                    painter.setFont(font)
                    text_rect = QRectF(center.x() + width/2 - 25, y_pos - 8, 20, 16)
                    painter.drawText(text_rect, Qt.AlignCenter, str(angle))

    def _draw_vertical_marks(self, painter: QPainter, center: QPointF, width: float, height: float, is_left: bool = True) -> None:
        # ...existing code...
        painter.setPen(QPen(Qt.white, 1))
        for angle in range(0, 61, 5):
            normalized_angle = (60 - angle) / 60.0
            y_pos = center.y() - height/2 * 0.7 + normalized_angle * height * 0.7
            if angle % 15 == 0:
                mark_width = width * 0.3
                painter.setPen(QPen(Qt.white, 2))
            elif angle % 10 == 0:
                mark_width = width * 0.2
                painter.setPen(QPen(Qt.white, 1.5))
            else:
                mark_width = width * 0.1
                painter.setPen(QPen(Qt.white, 1))
            start_x = center.x() - mark_width/2
            end_x = center.x() + mark_width/2
            painter.drawLine(QPointF(start_x, y_pos), QPointF(end_x, y_pos))
            if angle % 15 == 0:
                font = painter.font()
                font.setPointSize(8)
                painter.setFont(font)
                text_rect = QRectF(center.x() + width/2 - 25, y_pos - 8, 20, 16)
                painter.drawText(text_rect, Qt.AlignCenter, str(angle))

    def _draw_half_circle(self, painter: QPainter, center: QPointF, radius: float, inner_circle: bool = False) -> None:
        # ...existing code...
        diameter = radius * 2
        rect = QRectF(
            center.x() - radius,
            center.y() - radius,
            diameter,
            diameter
        )
        painter.setPen(QPen(Qt.white, 2))
        if inner_circle and self._current_angle == self._aim_angle:
            painter.setBrush(QColor(0, 255, 0, 100))
        else:
            painter.setBrush(QColor(255, 255, 255, 100))
        painter.drawPie(rect, -5 * 16, 70 * 16)

    def _draw_angle_marks(self, painter: QPainter, center: QPointF, radius: float) -> None:
        # ...existing code...
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        for angle in range(-5, 65, 5):
            angle_rad = math.radians(angle)
            end_point = QPointF(center.x() + radius * math.cos(angle_rad), center.y() - radius * math.sin(angle_rad))
            if angle % 15 == 0:
                painter.setPen(QPen(Qt.white, 2))
                start_point = QPointF(center.x() + radius * 0.92 * math.cos(angle_rad), center.y() - radius * 0.92 * math.sin(angle_rad))
            else:
                painter.setPen(QPen(Qt.white, 1))
                start_point = QPointF(center.x() + radius * 0.96 * math.cos(angle_rad), center.y() - radius * 0.96 * math.sin(angle_rad))
            painter.drawLine(start_point, end_point)

    def _draw_pointer_triangle(self, painter: QPainter, center: QPointF, radius: float, angle_deg: float, size: float, inner_circle: bool = True) -> None:
        # ...existing code...
        angle_rad = math.radians(angle_deg)
        x1 = center.x() + radius * math.cos(angle_rad)
        y1 = center.y() - radius * math.sin(angle_rad)
        p1 = QPointF(x1, y1)
        angle1 = angle_rad + math.radians(30)
        angle2 = angle_rad - math.radians(30)
        x2 = x1 + size * math.cos(angle1)
        y2 = y1 - size * math.sin(angle1)
        x3 = x1 + size * math.cos(angle2)
        y3 = y1 - size * math.sin(angle2)
        p2 = QPointF(x2, y2)
        p3 = QPointF(x3, y3)
        painter.setPen(QPen(Qt.white, 2))
        painter.setBrush(Qt.red)
        painter.drawPolygon(p1, p2, p3)
        x4 = center.x() + radius * math.cos(angle_rad) * 1.1
        y4 = center.y() - radius * math.sin(angle_rad) * 1.1
        p4 = QPointF(x4, y4)
        text_rect = QRectF(p4.x() - 10, p4.y() - 10, 40, 20)
        painter.setPen(QPen(Qt.red, 20))
        painter.drawText(text_rect, Qt.AlignCenter, f"{angle_deg:.1f}°")

    def _draw_aim_icon(self, painter: QPainter, center: QPointF, radius: float, current_angle: float) -> None:
        # ...existing code...
        angle_rad = math.radians(current_angle)
        icon_size = radius / 2
        x = center.x() + radius * math.cos(angle_rad) - icon_size / 2
        y = center.y() - radius * math.sin(angle_rad) - icon_size / 2
        icon_path = resource_path(r"assets\Icons\missileIcon.png").replace("\\", "/")
        aim_icon = QPixmap(icon_path)
        if aim_icon.isNull():
            print(f"Error: Unable to load icon from {icon_path}")
            return
        painter.setRenderHints(
            QPainter.Antialiasing |
            QPainter.SmoothPixmapTransform |
            QPainter.HighQualityAntialiasing
        )
        scaled_icon = aim_icon.scaled(
            int(icon_size), int(icon_size),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation
        )
        painter.save()
        painter.translate(x + icon_size/2, y + icon_size/2)
        painter.rotate(44 - self._current_angle)
        painter.drawPixmap(int(-icon_size/2), int(-icon_size/2), scaled_icon)
        painter.restore()
        x4 = center.x() + radius * math.cos(angle_rad) * 1.36
        y4 = center.y() - radius * math.sin(angle_rad) * 1.36
        p4 = QPointF(x4, y4)
        text_rect = QRectF(p4.x() - 10, p4.y() - 10, 40, 20)
        painter.setPen(QPen(Qt.black, 20))
        painter.drawText(text_rect, Qt.AlignCenter, f"{current_angle:.1f}°")
