from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from ..widgets.features.compass_widget import AngleCompass
from ..widgets.features.vertical_compass_widget import VerticalCompassWidget
from ..widgets.features.numeric_display_widget import NumericDataWidget
from ..widgets.features.bullet_widget import BulletWidget
from ..widgets.components.custom_message_box_widget import CustomMessageBox
from ..widgets.components.buttons.isometric import ColoredSVGButton
from .effects.grid_background_renderer import GridBackgroundWidget
import achived.ui_config as config
import yaml
import random
import math
from common.utils import resource_path
from scipy.interpolate import CubicSpline
import numpy as np

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
