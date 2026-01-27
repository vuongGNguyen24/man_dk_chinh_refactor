# -*- coding: utf-8 -*-

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QGroupBox, QGraphicsOpacityEffect, QButtonGroup, QRadioButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QDoubleValidator, QPainter, QColor, QFont
import ui.ui_config as config
from common.utils import get_firing_table_interpolator, resource_path, load_firing_table
import yaml


class AngleInputDialog(QWidget):
    """Widget overlay để nhập khoảng cách và góc hướng - hiển thị trên tab thay vì window riêng."""
    
    # Signal để thông báo khi đóng dialog
    accepted = pyqtSignal()
    rejected = pyqtSignal()
    
    def __init__(self, side="Trái", current_distance=0, current_direction=0, is_left_side=True, parent=None):
        super().__init__(parent)
        self.side = side
        self.distance_value = current_distance
        self.direction_value = current_direction
        self.is_left_side = is_left_side  # True nếu giàn trái, False nếu giàn phải
        
        # Đọc giới hạn từ config
        self._load_limits_from_config()
        
        # Biến theo dõi bảng bắn được chọn (True = bảng bắn cao, False = bảng bắn thấp)
        self.use_high_table = False
        self._high_table_interpolator = None  # Cache interpolator bảng bắn cao
        
        # Làm cho widget này hiển thị trên tất cả widget khác
        self.setWindowFlags(Qt.Widget)
        
        self.setupUi()
    
    def _load_limits_from_config(self):
        """Đọc giới hạn góc tầm và góc hướng từ config.yaml"""
        try:
            with open(resource_path('config.yaml'), 'r', encoding='utf-8') as f:
                yaml_config = yaml.safe_load(f)
            
            # Giới hạn góc tầm
            elevation_limits = yaml_config.get('Widgets', {}).get('LimitAngles', {}).get('Elevation', [10, 70])
            self.elevation_min = elevation_limits[0] if len(elevation_limits) > 0 else 10
            self.elevation_max = elevation_limits[1] if len(elevation_limits) > 1 else 70
            
            # Giới hạn góc hướng (redlines) - khác nhau cho trái và phải
            if self.is_left_side:
                redlines = yaml_config.get('Widgets', {}).get('CompassLeft', {}).get('redlines', [60, 65])
            else:
                redlines = yaml_config.get('Widgets', {}).get('CompassRight', {}).get('redlines', [65, 60])
            
            # redlines[0] là giới hạn âm, redlines[1] là giới hạn dương
            self.direction_neg_limit = redlines[0] if len(redlines) > 0 else 60
            self.direction_pos_limit = redlines[1] if len(redlines) > 1 else 65
            
        except Exception as e:
            print(f"Lỗi đọc config.yaml: {e}")
            # Giá trị mặc định
            self.elevation_min = 10
            self.elevation_max = 60
            self.direction_neg_limit = 60
            self.direction_pos_limit = 65
    
    def reload_limits_for_side(self):
        """Tải lại giới hạn khi chuyển đổi giữa giàn trái/phải."""
        # Tải lại giới hạn từ config
        self._load_limits_from_config()
        
        # Cập nhật validator cho góc hướng với giới hạn mới
        direction_validator = QDoubleValidator(-float(self.direction_neg_limit), float(self.direction_pos_limit), 1)
        direction_validator.setNotation(QDoubleValidator.StandardNotation)
        self.direction_input.setValidator(direction_validator)
        
        # Cập nhật placeholder cho góc hướng
        self.direction_input.setPlaceholderText(f"Nhập góc hướng (-{self.direction_neg_limit} -> {self.direction_pos_limit})")
        
        # Cập nhật validator cho góc tầm
        self.elevation_validator = QDoubleValidator(float(self.elevation_min-10), float(self.elevation_max)+5, 2)
        self.elevation_validator.setNotation(QDoubleValidator.StandardNotation)
        
        # Cập nhật placeholder cho góc tầm nếu đang ở chế độ nhập góc tầm
        is_distance = config.ELEVATION_INPUT_FROM_DISTANCE_L if self.is_left_side else config.ELEVATION_INPUT_FROM_DISTANCE_R
        if not is_distance:
            self.distance_input.setPlaceholderText(f"Nhập góc tầm ({self.elevation_min} -> {self.elevation_max})")
        
    def paintEvent(self, event):
        """Vẽ background semi-transparent cho overlay."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ background mờ đục để làm nổi bật dialog
        painter.fillRect(self.rect(), QColor(0, 0, 0, 150))
    
    def setupUi(self):
        """Thiết lập giao diện dialog."""
        # Layout chính chiếm toàn bộ widget
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container widget cho dialog box (sẽ được center)
        dialog_container = QWidget()
        dialog_container.setMinimumWidth(600)
        dialog_container.setMaximumWidth(700)
        dialog_container.setFixedHeight(900)  # Chiều cao cố định
        
        layout = QVBoxLayout()
        layout.setSpacing(20)  # Tăng spacing giữa các group box
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Group box cho khoảng cách/góc tầm
        self.distance_group = QGroupBox("Khoảng cách (m)")
        distance_layout = QVBoxLayout()
        distance_layout.setSpacing(15)  # Tăng spacing giữa các phần tử
        
        # Nút chuyển đổi chế độ nhập: Khoảng cách / Góc tầm trực tiếp
        input_type_layout = QHBoxLayout()
        input_type_layout.setSpacing(15)
        
        self.input_type_label = QLabel()
        self.input_type_label.setMinimumHeight(45)
        self.input_type_label.setMaximumHeight(45)
        self.input_type_label.setMinimumWidth(200)
        self.update_input_type_label()
        input_type_layout.addWidget(self.input_type_label)
        
        self.toggle_input_type_button = QPushButton()
        self.update_input_type_button()
        self.toggle_input_type_button.clicked.connect(self.toggle_input_type)
        self.toggle_input_type_button.setMinimumWidth(200)
        self.toggle_input_type_button.setMinimumHeight(45)
        self.toggle_input_type_button.setMaximumHeight(45)
        input_type_layout.addWidget(self.toggle_input_type_button)
        
        distance_layout.addLayout(input_type_layout)
        distance_layout.addSpacing(8)
        
        self.distance_input = QLineEdit()
        self.distance_input.setPlaceholderText("Nhập khoảng cách (0 -> 10000)")
        self.distance_input.setText(str(self.distance_value))
        self.distance_input.setMinimumHeight(50)  # Chiều cao ô nhập
        self.distance_input.setMaximumHeight(50)  # Giới hạn chiều cao tối đa

        # Validator cho khoảng cách (0-10000 mét)
        self.distance_validator = QDoubleValidator(0.0, 10000.0, 1)
        self.distance_validator.setNotation(QDoubleValidator.StandardNotation)
        self.distance_input.setValidator(self.distance_validator)
        
        # Validator cho góc tầm (từ config)
        self.elevation_validator = QDoubleValidator(float(self.elevation_min), float(self.elevation_max), 2)
        self.elevation_validator.setNotation(QDoubleValidator.StandardNotation)
        
        distance_layout.addWidget(self.distance_input)
        distance_layout.addSpacing(12)  # Thêm khoảng cách giữa input và buttons
        
        # Widget container cho nút chuyển đổi chế độ Auto/Manual (để có thể ẩn/hiện)
        self.mode_button_container = QWidget()
        mode_button_layout = QHBoxLayout(self.mode_button_container)
        mode_button_layout.setContentsMargins(0, 0, 0, 0)
        mode_button_layout.setSpacing(15)
        
        self.mode_label = QLabel()
        self.mode_label.setMinimumHeight(45)  # Chiều cao label
        self.mode_label.setMaximumHeight(45)  # Giới hạn chiều cao
        self.mode_label.setMinimumWidth(180)  # Chiều rộng label
        self.update_mode_label()
        mode_button_layout.addWidget(self.mode_label)
        
        self.toggle_mode_button = QPushButton()
        self.update_mode_button()
        self.toggle_mode_button.clicked.connect(self.toggle_distance_mode)
        self.toggle_mode_button.setMinimumWidth(180)  # Chiều rộng tối thiểu
        self.toggle_mode_button.setMinimumHeight(45)  # Chiều cao
        self.toggle_mode_button.setMaximumHeight(45)  # Giới hạn chiều cao
        mode_button_layout.addWidget(self.toggle_mode_button)
        
        distance_layout.addWidget(self.mode_button_container)
        self.distance_group.setLayout(distance_layout)
        
        # Group box cho góc tầm preview với 2 ô
        self.elevation_preview_group = QGroupBox("Góc tầm tính toán")
        self.elevation_preview_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 13px;
                padding-top: 15px;
                padding-bottom: 10px;
                padding-left: 10px;
                padding-right: 10px;
                color: #cccccc;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #ffffff;
            }
        """)
        elevation_preview_layout = QHBoxLayout()
        elevation_preview_layout.setSpacing(15)
        
        # Ô bên trái - Ly giác (độ thập phân)
        decimal_container = QVBoxLayout()
        decimal_container.setSpacing(0)  # Không có khoảng cách giữa label và số
        
        decimal_label = QLabel("Ly giác")
        decimal_label.setAlignment(Qt.AlignCenter)
        decimal_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                background-color: #333333;
                border: 2px solid #0078d4;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                padding: 5px;
            }
        """)
        
        self.elevation_decimal_label = QLabel("--")
        self.elevation_decimal_label.setAlignment(Qt.AlignCenter)
        self.elevation_decimal_label.setMinimumHeight(60)
        self.elevation_decimal_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #0078d4;
                border: 2px solid #0078d4;
                border-top: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                padding: 10px;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        decimal_container.addWidget(decimal_label)
        decimal_container.addWidget(self.elevation_decimal_label)
        
        # Ô bên phải - Độ phút
        dms_container = QVBoxLayout()
        dms_container.setSpacing(0)  # Không có khoảng cách giữa label và số
        
        dms_label = QLabel("Độ phút (° ')")
        dms_label.setAlignment(Qt.AlignCenter)
        dms_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                background-color: #333333;
                border: 2px solid #0078d4;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                padding: 5px;
            }
        """)
        
        self.elevation_dms_label = QLabel("--")
        self.elevation_dms_label.setAlignment(Qt.AlignCenter)
        self.elevation_dms_label.setMinimumHeight(60)
        self.elevation_dms_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #0078d4;
                border: 2px solid #0078d4;
                border-top: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                padding: 10px;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        dms_container.addWidget(dms_label)
        dms_container.addWidget(self.elevation_dms_label)
        
        elevation_preview_layout.addLayout(decimal_container)
        elevation_preview_layout.addLayout(dms_container)
        self.elevation_preview_group.setLayout(elevation_preview_layout)
        
        # Group box cho khoảng cách preview khi nhập góc tầm (ngược với elevation_preview_group)
        self.distance_preview_group = QGroupBox("Khoảng cách bắn được")
        self.distance_preview_group.setStyleSheet("""
            QGroupBox {
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 13px;
                padding-top: 15px;
                padding-bottom: 10px;
                padding-left: 10px;
                padding-right: 10px;
                color: #cccccc;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #ffffff;
            }
        """)
        distance_preview_layout = QHBoxLayout()
        distance_preview_layout.setSpacing(15)
        
        # Hiển thị khoảng cách nội suy
        distance_value_container = QVBoxLayout()
        distance_value_container.setSpacing(0)
        
        distance_value_label = QLabel("Khoảng cách (m)")
        distance_value_label.setAlignment(Qt.AlignCenter)
        distance_value_label.setStyleSheet("""
            QLabel {
                color: #ffffff;
                font-size: 13px;
                font-weight: bold;
                background-color: #333333;
                border: 2px solid #0078d4;
                border-bottom: none;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                border-bottom-left-radius: 0px;
                border-bottom-right-radius: 0px;
                padding: 5px;
            }
        """)
        
        self.distance_preview_label = QLabel("--")
        self.distance_preview_label.setAlignment(Qt.AlignCenter)
        self.distance_preview_label.setMinimumHeight(60)
        self.distance_preview_label.setStyleSheet("""
            QLabel {
                background-color: #1a1a1a;
                color: #0078d4;
                border: 2px solid #0078d4;
                border-top: none;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                border-bottom-left-radius: 8px;
                border-bottom-right-radius: 8px;
                padding: 10px;
                font-size: 20px;
                font-weight: bold;
            }
        """)
        
        distance_value_container.addWidget(distance_value_label)
        distance_value_container.addWidget(self.distance_preview_label)
        distance_preview_layout.addLayout(distance_value_container)
        
        self.distance_preview_group.setLayout(distance_preview_layout)
        self.distance_preview_group.setVisible(False)  # Mặc định ẩn, chỉ hiện khi nhập góc tầm
        
        # Widget container cho chọn bảng bắn cao/thấp (chỉ hiển thị khi khoảng cách >= 9100)
        self.table_selection_container = QWidget()
        self.table_selection_container.setStyleSheet("""
            QWidget {
                background-color: transparent;
                border: none;
            }
        """)
        table_selection_layout = QHBoxLayout(self.table_selection_container)
        table_selection_layout.setContentsMargins(10, 5, 10, 5)
        table_selection_layout.setSpacing(20)
        
        table_selection_label = QLabel("Chọn bảng bắn:")
        table_selection_label.setStyleSheet("""
            QLabel {
                color: white;
                font-size: 13px;
                font-weight: bold;
                background-color: transparent;
                border: none;
            }
        """)
        table_selection_layout.addWidget(table_selection_label)
        
        # Radio buttons cho bảng bắn - style đơn giản màu trắng
        self.table_button_group = QButtonGroup(self)
        
        radio_style = """
            QRadioButton {
                color: white;
                font-size: 13px;
                background-color: transparent;
                padding: 5px 10px;
                border: none;
            }
            QRadioButton::indicator {
                width: 16px;
                height: 16px;
            }
            QRadioButton::indicator:checked {
                background-color: white;
                border: 2px solid white;
                border-radius: 8px;
            }
            QRadioButton::indicator:unchecked {
                background-color: transparent;
                border: 2px solid white;
                border-radius: 8px;
            }
        """
        
        self.low_table_radio = QRadioButton("Bảng bắn thấp")
        self.low_table_radio.setChecked(True)
        self.low_table_radio.setStyleSheet(radio_style)
        
        self.high_table_radio = QRadioButton("Bảng bắn cao")
        self.high_table_radio.setStyleSheet(radio_style)
        
        self.table_button_group.addButton(self.low_table_radio, 0)
        self.table_button_group.addButton(self.high_table_radio, 1)
        
        table_selection_layout.addWidget(self.low_table_radio)
        table_selection_layout.addWidget(self.high_table_radio)
        table_selection_layout.addStretch()
        
        # Kết nối signal khi thay đổi bảng bắn
        self.table_button_group.buttonClicked.connect(self.on_table_selection_changed)
        
        # Ẩn mặc định, chỉ hiện khi khoảng cách > 9100
        self.table_selection_container.setVisible(False)
        
        # Cập nhật UI dựa trên chế độ nhập (khoảng cách hay góc tầm)
        self.update_input_type_ui()
        
        # Kết nối signal để cập nhật góc tầm khi thay đổi khoảng cách
        self.distance_input.textChanged.connect(self.update_elevation_preview)
        # Kết nối signal để cập nhật khoảng cách preview khi thay đổi góc tầm
        self.distance_input.textChanged.connect(self.update_distance_preview)
        
        # Group box cho góc hướng
        direction_group = QGroupBox("Góc hướng (độ)")
        direction_layout = QVBoxLayout()
        direction_layout.setSpacing(15)  # Tăng spacing giữa các phần tử
        
        self.direction_input = QLineEdit()
        # Placeholder với giới hạn từ config (âm -> dương)
        self.direction_input.setPlaceholderText(f"Nhập góc hướng (-{self.direction_neg_limit} -> {self.direction_pos_limit})")
        # Không set text mặc định để placeholder hiển thị
        self.direction_input.setMinimumHeight(50)  # Chiều cao ô nhập
        self.direction_input.setMaximumHeight(50)  # Giới hạn chiều cao
        
        # Validator cho góc hướng (từ config)
        direction_validator = QDoubleValidator(-float(self.direction_neg_limit), float(self.direction_pos_limit), 1)
        direction_validator.setNotation(QDoubleValidator.StandardNotation)
        self.direction_input.setValidator(direction_validator)
        
        direction_layout.addWidget(self.direction_input)
        direction_layout.addSpacing(12)  # Thêm khoảng cách giữa input và buttons
        
        # Nút chuyển đổi chế độ Auto/Manual cho góc hướng
        direction_mode_button_layout = QHBoxLayout()
        direction_mode_button_layout.setSpacing(15)
        
        self.direction_mode_label = QLabel()
        self.direction_mode_label.setMinimumHeight(45)  # Chiều cao label
        self.direction_mode_label.setMaximumHeight(45)  # Giới hạn chiều cao
        self.direction_mode_label.setMinimumWidth(180)  # Chiều rộng label
        self.update_direction_mode_label()
        direction_mode_button_layout.addWidget(self.direction_mode_label)
        
        self.toggle_direction_mode_button = QPushButton()
        self.update_direction_mode_button()
        self.toggle_direction_mode_button.clicked.connect(self.toggle_direction_mode)
        self.toggle_direction_mode_button.setMinimumWidth(180)  # Chiều rộng tối thiểu
        self.toggle_direction_mode_button.setMinimumHeight(45)  # Chiều cao
        self.toggle_direction_mode_button.setMaximumHeight(45)  # Giới hạn chiều cao
        direction_mode_button_layout.addWidget(self.toggle_direction_mode_button)
        
        direction_layout.addLayout(direction_mode_button_layout)
        direction_group.setLayout(direction_layout)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.ok_button = QPushButton("Xác nhận")
        self.ok_button.clicked.connect(self.accept)
        
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        
        # Title label
        title_label = QLabel(f"Nhập góc - Giàn {self.side}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: white;
            padding: 10px;
        """)
        
        # Add all to dialog container layout
        layout.addWidget(title_label)
        layout.addWidget(self.distance_group)
        layout.addWidget(self.elevation_preview_group)
        layout.addWidget(self.distance_preview_group)  # Thêm distance preview
        layout.addWidget(self.table_selection_container)  # Thêm widget chọn bảng bắn
        layout.addWidget(direction_group)
        layout.addSpacing(10)
        layout.addLayout(button_layout)
        
        dialog_container.setLayout(layout)
        
        # Thêm container vào main layout và center nó
        main_layout.addStretch()
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(dialog_container)
        h_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()
        
        self.setLayout(main_layout)
        
        # Style - cải thiện để dễ nhìn hơn
        dialog_container.setStyleSheet("""
            QWidget {
                background-color: #1a1a1a;
                border: 2px solid #0078d4;
                border-radius: 10px;
            }
            QGroupBox {
                border: 2px solid #444;
                border-radius: 8px;
                margin-top: 15px;
                font-weight: bold;
                font-size: 13px;
                padding-top: 15px;
                padding-bottom: 10px;
                padding-left: 10px;
                padding-right: 10px;
                color: #cccccc;
                background-color: transparent;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px;
                color: #ffffff;
            }
            QLabel {
                color: #aaaaaa;
                font-size: 13px;
                font-weight: normal;
                background-color: transparent;
            }
            QLineEdit {
                background-color: #f0f0f0;
                color: #000000;
                border: 2px solid #666666;
                border-radius: 5px;
                padding: 15px 20px;
                font-size: 14px;
                font-weight: normal;
                selection-background-color: #0078d4;
                selection-color: white;
            }
            QLineEdit::placeholder {
                font-size: 12px;
                font-weight: normal;
                color: #888888;
            }
            QLineEdit:focus {
                border: 3px solid #0078d4;
                background-color: #ffffff;
            }
            QLineEdit:hover {
                border: 2px solid #888888;
                background-color: #fafafa;
            }
            QLineEdit:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 25px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006bb3;
            }
        """)
        
        # Style cho nút Xác nhận (màu xanh dương)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 25px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006bb3;
            }
        """)
        
        # Style cho nút Hủy (nền đen, viền xanh)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #1a1a1a;
                color: white;
                border: 2px solid #0078d4;
                border-radius: 5px;
                padding: 10px 25px;
                font-size: 13px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2a2a2a;
                border-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #000000;
                border-color: #006bb3;
            }
        """)
        
        # Cập nhật góc tầm preview ban đầu
        self.update_elevation_preview()
        
        # Cập nhật chế độ góc hướng ban đầu
        self.update_direction_mode_label()
        self.update_direction_mode_button()
        
    def decimal_to_degrees_minutes(self, decimal_degrees):
        """Chuyển đổi từ độ thập phân sang độ phút.
        
        Args:
            decimal_degrees: Góc theo độ thập phân (ví dụ: 15.5)
            
        Returns:
            tuple: (độ, phút) - ví dụ: (15, 30)
        """
        degrees = int(decimal_degrees)
        minutes = (decimal_degrees - degrees) * 60
        return degrees, minutes
    
    def update_elevation_preview(self):
        """Cập nhật góc tầm preview khi khoảng cách thay đổi."""
        try:
            distance_text = self.distance_input.text()
            if not distance_text:
                self.elevation_decimal_label.setText("--")
                self.elevation_dms_label.setText("--")
                self.table_selection_container.setVisible(False)
                return
            
            distance = float(distance_text)
            
            # Hiển thị/ẩn widget chọn bảng bắn dựa trên khoảng cách
            if distance >= 9100:
                self.table_selection_container.setVisible(True)
            else:
                self.table_selection_container.setVisible(False)
                # Reset về bảng bắn thấp khi khoảng cách < 9100
                self.low_table_radio.setChecked(True)
                self.use_high_table = False
            
            # Chọn interpolator dựa trên bảng bắn được chọn
            if self.use_high_table and distance >= 9100:
                interpolator = self._get_high_table_interpolator()
            else:
                interpolator = get_firing_table_interpolator()
            
            if interpolator:
                # Lấy ly giác (chưa chuyển sang độ)
                elevation_mils = interpolator.interpolate_angle_mils(distance)
                # Lấy góc độ (đã chuyển sang độ)
                elevation_angle = interpolator.interpolate_angle(distance)
                
                # Chuyển đổi sang độ phút
                degrees, minutes = self.decimal_to_degrees_minutes(elevation_angle)
                
                # Hiển thị ly giác và độ phút với 2 chữ số thập phân
                self.elevation_decimal_label.setText(f"{elevation_mils:.2f}")
                self.elevation_dms_label.setText(f"{degrees}° {minutes:.2f}'")
            else:
                self.elevation_decimal_label.setText("N/A")
                self.elevation_dms_label.setText("N/A")
        except ValueError:
            self.elevation_decimal_label.setText("--")
            self.elevation_dms_label.setText("--")
            self.table_selection_container.setVisible(False)
    
    def update_distance_preview(self):
        """Cập nhật khoảng cách preview khi góc tầm thay đổi."""
        try:
            elevation_text = self.distance_input.text()
            if not elevation_text:
                self.distance_preview_label.setText("--")
                return
            
            elevation = float(elevation_text)
            
            # Lấy interpolator (sử dụng bảng bắn thấp mặc định cho góc tầm trực tiếp)
            interpolator = get_firing_table_interpolator()
            
            if interpolator:
                # Nội suy ngược: từ góc tầm -> khoảng cách
                distance = interpolator.interpolate_range_from_angle(elevation)
                
                # Hiển thị khoảng cách với 2 chữ số thập phân
                self.distance_preview_label.setText(f"{distance:.2f}")
            else:
                self.distance_preview_label.setText("N/A")
        except ValueError:
            self.distance_preview_label.setText("--")
    
    def _get_high_table_interpolator(self):
        """Lấy hoặc tạo interpolator cho bảng bắn cao."""
        if self._high_table_interpolator is None:
            self._high_table_interpolator = load_firing_table("table1_high.csv")
        return self._high_table_interpolator
    
    def on_table_selection_changed(self, button):
        """Xử lý khi người dùng thay đổi lựa chọn bảng bắn."""
        self.use_high_table = (button == self.high_table_radio)
        # Cập nhật lại góc tầm preview
        self.update_elevation_preview()
    
    def toggle_distance_mode(self):
        """Chuyển đổi giữa chế độ tự động và thủ công."""
        is_distance = config.ELEVATION_INPUT_FROM_DISTANCE_L if self.is_left_side else config.ELEVATION_INPUT_FROM_DISTANCE_R
        
        if is_distance:
            # Đang ở chế độ nhập khoảng cách -> toggle DISTANCE_MODE_AUTO
            if self.is_left_side:
                config.DISTANCE_MODE_AUTO_L = not config.DISTANCE_MODE_AUTO_L
            else:
                config.DISTANCE_MODE_AUTO_R = not config.DISTANCE_MODE_AUTO_R
        else:
            # Đang ở chế độ nhập góc tầm trực tiếp -> toggle ELEVATION_MODE_AUTO
            if self.is_left_side:
                config.ELEVATION_MODE_AUTO_L = not config.ELEVATION_MODE_AUTO_L
            else:
                config.ELEVATION_MODE_AUTO_R = not config.ELEVATION_MODE_AUTO_R
        
        self.update_mode_label()
        self.update_mode_button()
    
    def toggle_input_type(self):
        """Chuyển đổi giữa chế độ nhập khoảng cách và nhập góc tầm trực tiếp."""
        if self.is_left_side:
            config.ELEVATION_INPUT_FROM_DISTANCE_L = not config.ELEVATION_INPUT_FROM_DISTANCE_L
        else:
            config.ELEVATION_INPUT_FROM_DISTANCE_R = not config.ELEVATION_INPUT_FROM_DISTANCE_R
        
        self.update_input_type_label()
        self.update_input_type_button()
        self.update_input_type_ui()
    
    def update_input_type_label(self):
        """Cập nhật label hiển thị kiểu nhập hiện tại."""
        is_distance = config.ELEVATION_INPUT_FROM_DISTANCE_L if self.is_left_side else config.ELEVATION_INPUT_FROM_DISTANCE_R
        if is_distance:
            mode_text = "Nhập: <b>Khoảng cách</b>"
        else:
            mode_text = "Nhập: <b>Góc tầm trực tiếp</b>"
        
        self.input_type_label.setText(mode_text)
        self.input_type_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 15px;
                background-color: #1a1a1a;
                border: 2px solid #0078d4;
                border-radius: 5px;
            }
        """)
    
    def update_input_type_button(self):
        """Cập nhật text và style của nút chuyển kiểu nhập."""
        is_distance = config.ELEVATION_INPUT_FROM_DISTANCE_L if self.is_left_side else config.ELEVATION_INPUT_FROM_DISTANCE_R
        if is_distance:
            button_text = "Chuyển sang Góc tầm"
        else:
            button_text = "Chuyển sang Khoảng cách"
        
        self.toggle_input_type_button.setText(button_text)
        self.toggle_input_type_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006bb3;
            }
        """)
    
    def update_input_type_ui(self):
        """Cập nhật giao diện dựa trên kiểu nhập (khoảng cách hay góc tầm)."""
        is_distance = config.ELEVATION_INPUT_FROM_DISTANCE_L if self.is_left_side else config.ELEVATION_INPUT_FROM_DISTANCE_R
        
        # Xóa text cũ trước khi chuyển đổi
        self.distance_input.clear()
        
        if is_distance:
            # Chế độ nhập khoảng cách
            self.distance_group.setTitle("Khoảng cách (m)")
            self.distance_input.setPlaceholderText("Nhập khoảng cách (0 -> 10000)")
            self.distance_input.setValidator(self.distance_validator)
            # Chỉ hiển thị giá trị khoảng cách nếu khác 0
            current_distance = config.DISTANCE_L if self.is_left_side else config.DISTANCE_R
            if current_distance != 0:
                self.distance_input.setText(str(current_distance))
            self.elevation_preview_group.setVisible(True)
            self.distance_preview_group.setVisible(False)
            self.elevation_preview_group.setTitle("Góc tầm tính toán")
            # Hiển thị phần chọn chế độ tự động/thủ công
            self.mode_button_container.setVisible(True)
            # Kích hoạt/vô hiệu hóa ô nhập dựa trên chế độ tự động/thủ công
            is_auto = config.DISTANCE_MODE_AUTO_L if self.is_left_side else config.DISTANCE_MODE_AUTO_R
            self.distance_input.setEnabled(not is_auto)
        else:
            # Chế độ nhập góc tầm trực tiếp
            self.distance_group.setTitle("Góc tầm (độ)")
            self.distance_input.setPlaceholderText(f"Nhập góc tầm ({self.elevation_min} -> {self.elevation_max})")
            self.distance_input.setValidator(self.elevation_validator)
            # Hiển thị góc tầm hiện tại nếu khác 0
            current_elevation = config.ANGLE_L if self.is_left_side else config.ANGLE_R
            if current_elevation != 0:
                self.distance_input.setText(str(current_elevation))
            self.elevation_preview_group.setVisible(False)
            self.distance_preview_group.setVisible(True)
            # Hiển thị phần chọn chế độ tự động/thủ công cho góc tầm
            self.mode_button_container.setVisible(True)
            # Kích hoạt/vô hiệu hóa ô nhập dựa trên chế độ tự động/thủ công của góc tầm
            is_auto = config.ELEVATION_MODE_AUTO_L if self.is_left_side else config.ELEVATION_MODE_AUTO_R
            self.distance_input.setEnabled(not is_auto)
        
        # Cập nhật label và button mode
        self.update_mode_label()
        self.update_mode_button()
        
        # Cập nhật lại preview nếu đang ở chế độ khoảng cách
        if is_distance:
            self.update_elevation_preview()
        
    def toggle_direction_mode(self):
        """Chuyển đổi giữa chế độ tự động và thủ công cho góc hướng."""
        if self.is_left_side:
            config.DIRECTION_MODE_AUTO_L = not config.DIRECTION_MODE_AUTO_L
        else:
            config.DIRECTION_MODE_AUTO_R = not config.DIRECTION_MODE_AUTO_R
        
        self.update_direction_mode_label()
        self.update_direction_mode_button()
        
    def update_mode_label(self):
        """Cập nhật label hiển thị chế độ hiện tại."""
        is_distance = config.ELEVATION_INPUT_FROM_DISTANCE_L if self.is_left_side else config.ELEVATION_INPUT_FROM_DISTANCE_R
        
        if is_distance:
            # Chế độ nhập khoảng cách
            is_auto = config.DISTANCE_MODE_AUTO_L if self.is_left_side else config.DISTANCE_MODE_AUTO_R
        else:
            # Chế độ nhập góc tầm trực tiếp
            is_auto = config.ELEVATION_MODE_AUTO_L if self.is_left_side else config.ELEVATION_MODE_AUTO_R
        
        mode_text = "Chế độ: <b>Tự động</b>" if is_auto else "Chế độ: <b>Thủ công</b>"
        self.mode_label.setText(mode_text)
        self.mode_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 15px;
                background-color: #1a1a1a;
                border: 2px solid #0078d4;
                border-radius: 5px;
            }
        """)
        
        # Vô hiệu hóa/kích hoạt ô nhập dựa trên chế độ
        self.distance_input.setEnabled(not is_auto)
        
    def update_mode_button(self):
        """Cập nhật text và style của nút chuyển chế độ."""
        is_distance = config.ELEVATION_INPUT_FROM_DISTANCE_L if self.is_left_side else config.ELEVATION_INPUT_FROM_DISTANCE_R
        
        if is_distance:
            # Chế độ nhập khoảng cách
            is_auto = config.DISTANCE_MODE_AUTO_L if self.is_left_side else config.DISTANCE_MODE_AUTO_R
        else:
            # Chế độ nhập góc tầm trực tiếp
            is_auto = config.ELEVATION_MODE_AUTO_L if self.is_left_side else config.ELEVATION_MODE_AUTO_R
        
        button_text = "Chuyển sang Thủ công" if is_auto else "Chuyển sang Tự động"
        self.toggle_mode_button.setText(button_text)
        
        self.toggle_mode_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006bb3;
            }
        """)
        
    def update_direction_mode_label(self):
        """Cập nhật label hiển thị chế độ hiện tại cho góc hướng."""
        is_auto = config.DIRECTION_MODE_AUTO_L if self.is_left_side else config.DIRECTION_MODE_AUTO_R
        mode_text = "Chế độ: <b>Tự động</b>" if is_auto else "Chế độ: <b>Thủ công</b>"
        self.direction_mode_label.setText(mode_text)
        self.direction_mode_label.setStyleSheet("""
            QLabel {
                color: #0078d4;
                font-size: 13px;
                font-weight: bold;
                padding: 10px 15px;
                background-color: #1a1a1a;
                border: 2px solid #0078d4;
                border-radius: 5px;
            }
        """)
        
        # Vô hiệu hóa/kích hoạt ô nhập góc hướng dựa trên chế độ
        self.direction_input.setEnabled(not is_auto)
        
    def update_direction_mode_button(self):
        """Cập nhật text và style của nút chuyển chế độ cho góc hướng."""
        is_auto = config.DIRECTION_MODE_AUTO_L if self.is_left_side else config.DIRECTION_MODE_AUTO_R
        button_text = "Chuyển sang Thủ công" if is_auto else "Chuyển sang Tự động"
        self.toggle_direction_mode_button.setText(button_text)
        
        self.toggle_direction_mode_button.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1084d8;
            }
            QPushButton:pressed {
                background-color: #006bb3;
            }
        """)
    
    def accept(self):
        """Xử lý khi nhấn nút Xác nhận."""
        self.accepted.emit()
        self.hide()
    
    def reject(self):
        """Xử lý khi nhấn nút Hủy."""
        self.rejected.emit()
        self.hide()
        
    def get_values(self):
        """Lấy giá trị khoảng cách/góc tầm và góc hướng đã nhập.
        
        Returns:
            tuple: (distance_or_elevation, direction, is_direct_elevation, use_high_table)
                - distance_or_elevation: khoảng cách (m) hoặc góc tầm trực tiếp (độ)
                - direction: góc hướng (độ)
                - is_direct_elevation: True nếu đang nhập góc tầm trực tiếp, False nếu nhập khoảng cách
                - use_high_table: True nếu sử dụng bảng bắn cao, False nếu bảng bắn thấp
        """
        try:
            is_direct_elevation = not (config.ELEVATION_INPUT_FROM_DISTANCE_L if self.is_left_side else config.ELEVATION_INPUT_FROM_DISTANCE_R)
            
            # Lấy giá trị input (khoảng cách hoặc góc tầm)
            if is_direct_elevation:
                # Chế độ nhập góc tầm trực tiếp
                is_auto = config.ELEVATION_MODE_AUTO_L if self.is_left_side else config.ELEVATION_MODE_AUTO_R
                if is_auto:
                    # Chế độ tự động - lấy giá trị góc tầm hiện tại từ CAN
                    input_value = config.ANGLE_L if self.is_left_side else config.ANGLE_R
                else:
                    # Chế độ thủ công - lấy từ ô nhập, nếu trống thì giữ nguyên giá trị AIM_ANGLE hiện tại
                    if self.distance_input.text():
                        input_value = float(self.distance_input.text())
                    else:
                        # Nếu ô nhập trống, giữ nguyên góc tầm mục tiêu hiện tại
                        input_value = config.AIM_ANGLE_L if self.is_left_side else config.AIM_ANGLE_R
                # Clamp theo giới hạn từ config
                input_value = max(float(self.elevation_min), min(float(self.elevation_max), input_value))
            else:
                # Chế độ nhập khoảng cách
                is_auto = config.DISTANCE_MODE_AUTO_L if self.is_left_side else config.DISTANCE_MODE_AUTO_R
                if is_auto:
                    # Chế độ tự động - lấy giá trị khoảng cách hiện tại từ CAN
                    input_value = config.DISTANCE_L if self.is_left_side else config.DISTANCE_R
                else:
                    # Chế độ thủ công - lấy từ ô nhập, nếu trống thì giữ nguyên giá trị DISTANCE hiện tại
                    if self.distance_input.text():
                        input_value = float(self.distance_input.text())
                    else:
                        # Nếu ô nhập trống, giữ nguyên khoảng cách hiện tại
                        input_value = config.DISTANCE_L if self.is_left_side else config.DISTANCE_R
                # Clamp theo giới hạn
                input_value = max(0.0, min(10000.0, input_value))
            
            # Lấy giá trị góc hướng
            is_direction_auto = config.DIRECTION_MODE_AUTO_L if self.is_left_side else config.DIRECTION_MODE_AUTO_R
            if is_direction_auto:
                # Chế độ tự động - lấy giá trị góc hướng hiện tại từ CAN
                direction = config.DIRECTION_L if self.is_left_side else config.DIRECTION_R
            else:
                # Chế độ thủ công - lấy từ ô nhập, nếu trống thì giữ nguyên giá trị AIM_DIRECTION hiện tại
                if self.direction_input.text():
                    direction = float(self.direction_input.text())
                else:
                    # Nếu ô nhập trống, giữ nguyên góc hướng mục tiêu hiện tại
                    direction = config.AIM_DIRECTION_L if self.is_left_side else config.AIM_DIRECTION_R
            
            # Clamp góc hướng theo giới hạn từ config
            direction = max(-float(self.direction_neg_limit), min(float(self.direction_pos_limit), direction))
            
            return input_value, direction, is_direct_elevation, self.use_high_table
        except ValueError:
            # Trả về giá trị mặc định nếu parse lỗi
            is_direct_elevation = not (config.ELEVATION_INPUT_FROM_DISTANCE_L if self.is_left_side else config.ELEVATION_INPUT_FROM_DISTANCE_R)
            return self.distance_value, self.direction_value, is_direct_elevation, self.use_high_table
