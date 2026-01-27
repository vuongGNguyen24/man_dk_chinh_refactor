# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QColor, QPen, QRadialGradient, QBrush
from PyQt5.QtCore import Qt, QRectF, QTimer


class StatusIndicatorWidget(QWidget):
    """Widget hiển thị 2 đèn trạng thái cho Nguồn và Sẵn sàng."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Trạng thái mặc định
        self.power_status = True  # True = xanh (bình thường), False = đỏ (bất thường)
        self.ready_status = True  # True = xanh (bình thường), False = đỏ (bất thường)
        
        # Animation cho đèn nhấp nháy
        self.blink_state = True
        self.blink_timer = QTimer()
        self.blink_timer.timeout.connect(self._toggle_blink)
        self.blink_timer.start(500)  # Nhấp nháy mỗi 500ms
        
        # Set size cố định
        self.setFixedSize(180, 120)
        
    def _toggle_blink(self):
        """Toggle trạng thái nhấp nháy."""
        self.blink_state = not self.blink_state
        self.update()
        
    def set_power_status(self, status: bool):
        """Cập nhật trạng thái nguồn.
        
        Args:
            status: True = xanh (bình thường), False = đỏ (bất thường)
        """
        self.power_status = status
        self.update()
        
    def set_ready_status(self, status: bool):
        """Cập nhật trạng thái sẵn sàng.
        
        Args:
            status: True = xanh (bình thường), False = đỏ (bất thường)
        """
        self.ready_status = status
        self.update()
        
    def paintEvent(self, event):
        """Vẽ 2 đèn trạng thái."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ background
        painter.fillRect(self.rect(), QColor(30, 30, 30, 200))
        painter.setPen(QPen(QColor(80, 80, 80), 2))
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 8, 8)
        
        # Vẽ đèn Nguồn
        self._draw_indicator(painter, 20, 20, self.power_status, "Nguồn")
        
        # Vẽ đèn Sẵn sàng
        self._draw_indicator(painter, 20, 70, self.ready_status, "Sẵn sàng")
        
    def _draw_indicator(self, painter: QPainter, x: int, y: int, status: bool, label: str):
        """Vẽ một đèn trạng thái.
        
        Args:
            painter: QPainter object
            x, y: Vị trí đèn
            status: True = xanh, False = đỏ
            label: Nhãn hiển thị
        """
        # Kích thước đèn
        light_size = 30
        
        # Màu sắc tùy theo trạng thái
        if status:
            # Xanh lá - bình thường
            base_color = QColor(40, 200, 40)
            glow_color = QColor(40, 255, 40, 150)
        else:
            # Đỏ - bất thường (nhấp nháy)
            if self.blink_state:
                base_color = QColor(220, 30, 30)
                glow_color = QColor(255, 40, 40, 180)
            else:
                base_color = QColor(120, 15, 15)
                glow_color = QColor(150, 20, 20, 100)
        
        # Vẽ glow effect (hào quang)
        glow_gradient = QRadialGradient(x + light_size/2, y + light_size/2, light_size)
        glow_gradient.setColorAt(0, glow_color)
        glow_gradient.setColorAt(0.5, QColor(glow_color.red(), glow_color.green(), glow_color.blue(), 50))
        glow_gradient.setColorAt(1, QColor(0, 0, 0, 0))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(glow_gradient))
        painter.drawEllipse(QRectF(x - 5, y - 5, light_size + 10, light_size + 10))
        
        # Vẽ đèn chính
        light_gradient = QRadialGradient(x + light_size/2, y + light_size/2, light_size/2)
        light_gradient.setColorAt(0, base_color.lighter(150))
        light_gradient.setColorAt(0.6, base_color)
        light_gradient.setColorAt(1, base_color.darker(120))
        
        painter.setBrush(QBrush(light_gradient))
        painter.drawEllipse(QRectF(x, y, light_size, light_size))
        
        # Vẽ viền đèn
        painter.setPen(QPen(QColor(60, 60, 60), 2))
        painter.setBrush(Qt.NoBrush)
        painter.drawEllipse(QRectF(x, y, light_size, light_size))
        
        # Vẽ highlight shine
        shine_gradient = QRadialGradient(x + light_size * 0.3, y + light_size * 0.3, light_size * 0.3)
        shine_gradient.setColorAt(0, QColor(255, 255, 255, 100))
        shine_gradient.setColorAt(1, QColor(255, 255, 255, 0))
        
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(shine_gradient))
        painter.drawEllipse(QRectF(x + 5, y + 5, light_size * 0.4, light_size * 0.4))
        
        # Vẽ label
        painter.setPen(QPen(Qt.white, 1))
        font = painter.font()
        font.setPointSize(10)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(QRectF(x + light_size + 10, y, 90, light_size), 
                        Qt.AlignVCenter | Qt.AlignLeft, label)
