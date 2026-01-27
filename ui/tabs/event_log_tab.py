from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from ..widgets.compass_widget import AngleCompass
from ..widgets.half_compass_widget import HalfCircleWidget
from ..widgets.numeric_display_widget import NumericDataWidget
from ..widgets.ammunition_widget import BulletWidget
from ..widgets.custom_message_box_widget import CustomMessageBox
from ..components.ui_utilities import ColoredSVGButton
import ui.ui_config as config
import yaml
import random
import math
from common.utils import resource_path
from scipy.interpolate import CubicSpline
import numpy as np

class GridBackgroundWidget(QtWidgets.QWidget):
    """Widget với grid background cho toàn bộ app với hiệu ứng dot nhấp nháy."""
    
    def __init__(self, parent=None, enable_animation=True):
        super().__init__(parent)
        self.enable_animation = enable_animation
        self.grid_spacing = 50
        self.dot_clusters = []
        self.animation_timer = QtCore.QTimer()
        self.animation_timer.timeout.connect(self.update_animation)
        if self.enable_animation:
            self.animation_timer.start(50)  # Giảm xuống 50ms để animation mượt hơn
        self.time_offset = 0
        self._initialize_dot_clusters()
    
    def set_animation_enabled(self, enabled):
        """Bật/tắt hiệu ứng animation."""
        self.enable_animation = enabled
        if enabled:
            self.animation_timer.start(50)
        else:
            self.animation_timer.stop()
        self.update()  # Cập nhật để vẽ lại
        
    def _initialize_dot_clusters(self):
        """Khởi tạo hiệu ứng sóng từ trái trên xuống phải dưới."""
        # Không cần clusters nữa, chỉ cần thông số sóng
        self.wave_speed = 0.05  # Tăng tốc độ sóng chạy để rõ ràng hơn
        self.wave_frequency = 0.5  # Tăng tần số để tạo sự khác biệt rõ rệt giữa các dot
        
    def update_animation(self):
        """Cập nhật animation cho dot nhấp nháy."""
        if self.enable_animation:
            self.time_offset += 1
            self.update()  # Trigger repaint
        
    def paintEvent(self, event):
        """Vẽ grid background với dot nhấp nháy."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        if not self.enable_animation:
            # Chỉ vẽ background đơn giản nếu animation bị tắt
            return
        
        # Vẽ lưới background với đường kẻ ngang và dọc màu xám trắng mỏng
        painter.setPen(QPen(QColor(220, 220, 220, 80), 0.5))
        
        # Vẽ các đường kẻ dọc
        for x in range(0, self.width(), self.grid_spacing):
            painter.drawLine(x, 0, x, self.height())
        
        # Vẽ các đường kẻ ngang
        for y in range(0, self.height(), self.grid_spacing):
            painter.drawLine(0, y, self.width(), y)
            
        # Vẽ các dot nhấp nháy tại giao điểm
        self._draw_blinking_dots(painter)
        
    def _draw_blinking_dots(self, painter):
        """Vẽ các dot nhấp nháy theo dạng sóng từ trái trên xuống phải dưới."""
        painter.setPen(Qt.NoPen)
        
        # Tính toán số lượng giao điểm
        cols = self.width() // self.grid_spacing + 1
        rows = self.height() // self.grid_spacing + 1
        
        # Tạo danh sách tất cả giao điểm hợp lệ (tránh viền)
        margin = 20
        for row in range(rows):
            for col in range(cols):
                x = col * self.grid_spacing
                y = row * self.grid_spacing
                
                # Kiểm tra nếu giao điểm nằm trong vùng hợp lệ
                if margin <= x <= self.width() - margin and margin <= y <= self.height() - margin:
                    # Tính toán khoảng cách diagonal từ góc trái trên (0,0)
                    # Sử dụng tổng col + row để tạo diagonal
                    diagonal_distance = col + row
                    
                    # Tạo sóng chạy theo thời gian với công thức rõ ràng hơn
                    wave_phase = self.time_offset * self.wave_speed - diagonal_distance * self.wave_frequency
                    
                    # Tính alpha dựa trên sóng sin với biên độ lớn hơn
                    alpha = int(80 + 175 * math.sin(wave_phase))  # Alpha từ 80 đến 255 để rõ ràng hơn
                    
                    # Đảm bảo alpha trong khoảng hợp lệ
                    alpha = max(0, min(255, alpha))
                    
                    # Màu dot: xanh lam nhạt với alpha theo sóng
                    color = QColor(100, 150, 255, alpha)
                    painter.setBrush(QBrush(color))
                    
                    # Vẽ dot nhỏ tại chính xác giao điểm
                    dot_size = 2.5
                    dot_rect = QRectF(
                        x - dot_size/2, 
                        y - dot_size/2,
                        dot_size, 
                        dot_size
                    )
                    painter.drawEllipse(dot_rect)
                        
    def resizeEvent(self, event):
        """Khởi tạo lại dot clusters khi resize."""
        super().resizeEvent(event)
        self._initialize_dot_clusters()

class LogTab(GridBackgroundWidget):
    _instance = None  # Singleton instance
    _fire_control_instance = None  # Reference đến FireControl để hiển thị error indicator
    
    def __init__(self, config_data, parent=None):
        super().__init__(parent, enable_animation=config_data['MainWindow'].get('background_animation', True))
        self.config = config_data
        LogTab._instance = self  # Lưu instance để có thể truy cập toàn cục
        self.setupUi()
    
    @staticmethod
    def set_fire_control_instance(fire_control):
        """Lưu reference đến FireControl instance."""
        LogTab._fire_control_instance = fire_control

    def setupUi(self):
        # Create main layout for log display
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(10, 10, 10, 10)
        self.setLayout(main_layout)
        
        # Add a label to indicate this is the log tab
        log_label = QtWidgets.QLabel("Lịch sử sự kiện")
        log_label.setStyleSheet("""
            QLabel {
                color: #F1F5F9;
                font-size: 18px;
                font-weight: bold;
                padding: 15px;
                background: #19232D;
                border: 2px solid #10B981;
                border-radius: 8px;
                margin-bottom: 10px;
            }
        """)
        log_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(log_label)
        
        # Create text browser for displaying logs
        self.log_browser = QtWidgets.QTextBrowser()
        self.log_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #1E293B;
                color: #F1F5F9;
                font-size: 13px;
                font-family: 'Courier New', monospace;
                padding: 10px;
                border: 2px solid #475569;
                border-radius: 8px;
            }
        """)
        main_layout.addWidget(self.log_browser)
        
        # Add clear button
        clear_btn = QtWidgets.QPushButton("Xóa lịch sử")
        clear_btn.setFixedHeight(40)
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: #F1F5F9;
                font-size: 14px;
                font-weight: bold;
                border: none;
                border-radius: 8px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
            QPushButton:pressed {
                background-color: #991B1B;
            }
        """)
        clear_btn.clicked.connect(self.clear_logs)
        main_layout.addWidget(clear_btn)
    
    def add_log(self, message, level="INFO"):
        """Thêm log message vào log browser.
        
        Args:
            message: Nội dung log
            level: Mức độ log (INFO, WARNING, ERROR)
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Định dạng màu theo level
        if level == "ERROR":
            color = "#EF4444"  # Đỏ
            icon = "❌"
            # Hiển thị chấm đỏ trên tab lịch sử khi có ERROR
            if LogTab._fire_control_instance:
                try:
                    LogTab._fire_control_instance.show_error_indicator()
                except Exception as e:
                    print(f"Không thể hiển thị error indicator: {e}")
        elif level == "WARNING":
            color = "#F59E0B"  # Vàng
            icon = "⚠️"
        elif level == "SUCCESS":
            color = "#10B981"  # Xanh lá
            icon = "✅"
        else:  # INFO
            color = "#3B82F6"  # Xanh dương
            icon = "ℹ️"
        
        # Thêm HTML formatted log
        log_html = f'<span style="color: #94A3B8;">[{timestamp}]</span> <span style="color: {color};">{icon} [{level}]</span> {message}'
        self.log_browser.append(log_html)
        
        # Scroll to bottom
        self.log_browser.verticalScrollBar().setValue(
            self.log_browser.verticalScrollBar().maximum()
        )
    
    def clear_logs(self):
        """Xóa tất cả logs."""
        self.log_browser.clear()
        self.add_log("Đã xóa lịch sử sự kiện", "INFO")
    
    @staticmethod
    def get_instance():
        """Lấy instance của LogTab."""
        return LogTab._instance
    
    @staticmethod
    def log(message, level="INFO"):
        """Static method để ghi log từ bất kỳ đâu.
        
        Args:
            message: Nội dung log
            level: Mức độ log (INFO, WARNING, ERROR, SUCCESS)
        """
        instance = LogTab.get_instance()
        if instance:
            instance.add_log(message, level)
        else:
            print(f"[{level}] {message}")
