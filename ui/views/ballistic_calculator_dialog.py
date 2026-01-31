from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel,
                             QLineEdit, QPushButton, QWidget, QGridLayout, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QDoubleValidator, QIntValidator
import ui.ui_config as config
from communication.data_sender import sender_angle_direction


class ModeSelector(QWidget):
    """Widget chọn chế độ với radio buttons: Tự động, Bán tự động, Thủ công."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_mode = "auto"  # "auto", "semi-auto", "manual"
        self.setup_ui()
    
    def setup_ui(self):
        """Thiết lập giao diện."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("Chế độ tính toán")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #F1F5F9;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Container cho các radio buttons
        radio_container = QWidget()
        radio_layout = QHBoxLayout(radio_container)
        radio_layout.setContentsMargins(0, 0, 0, 0)
        radio_layout.setSpacing(15)
        
        # Tạo 3 radio buttons
        self.auto_radio = self.create_radio_button("Tự động", True)
        self.semi_auto_radio = self.create_radio_button("Bán tự động", False)
        self.manual_radio = self.create_radio_button("Thủ công", False)
        
        radio_layout.addWidget(self.auto_radio)
        radio_layout.addWidget(self.semi_auto_radio)
        radio_layout.addWidget(self.manual_radio)
        
        layout.addWidget(radio_container)
        
        # Connect signals
        self.auto_radio.clicked.connect(lambda: self.on_mode_changed("auto"))
        self.semi_auto_radio.clicked.connect(lambda: self.on_mode_changed("semi-auto"))
        self.manual_radio.clicked.connect(lambda: self.on_mode_changed("manual"))
    
    def create_radio_button(self, text, checked=False):
        """Tạo một radio button với styling tùy chỉnh."""
        from PyQt5.QtWidgets import QRadioButton
        
        radio = QRadioButton(text)
        radio.setChecked(checked)
        radio.setCursor(Qt.PointingHandCursor)
        radio.setStyleSheet("""
            QRadioButton {
                color: #F1F5F9;
                font-size: 13px;
                font-family: 'Tahoma', Arial, sans-serif;
                spacing: 8px;
            }
            QRadioButton::indicator {
                width: 20px;
                height: 20px;
                border-radius: 10px;
                border: 2px solid #64C8FF;
                background-color: transparent;
            }
            QRadioButton::indicator:checked {
                background-color: #64C8FF;
                border: 2px solid #64C8FF;
            }
            QRadioButton:hover {
                color: #FFFFFF;
            }
        """)
        return radio
    
    def on_mode_changed(self, mode):
        """Xử lý khi chế độ thay đổi."""
        self.current_mode = mode
        
        # Update checked state
        self.auto_radio.setChecked(mode == "auto")
        self.semi_auto_radio.setChecked(mode == "semi-auto")
        self.manual_radio.setChecked(mode == "manual")
        
        # Gọi callback nếu có
        if hasattr(self, 'on_mode_change_callback'):
            self.on_mode_change_callback(mode)
    
    def get_mode(self):
        """Lấy chế độ hiện tại."""
        return self.current_mode
    
    def set_mode(self, mode):
        """Set chế độ."""
        if mode in ["auto", "semi-auto", "manual"]:
            self.on_mode_changed(mode)


class BallisticCalculatorWidget(QWidget):
    """Widget tính toán lượng sửa bắn hiển thị inline trong giao diện."""

    def __init__(self, parent=None):
        super().__init__(parent)

        # Set object name để áp dụng stylesheet riêng
        self.setObjectName("ballistic_calculator_main")

        # Giá trị tiêu chuẩn
        self.standard_temp = 15.9
        self.standard_pressure = 750
        self.standard_charge_temp = 15

        # Lấy góc hiện tại từ config
        self.current_elevation_left = config.ANGLE_L
        self.current_direction_left = config.DIRECTION_L
        self.current_elevation_right = config.ANGLE_R
        self.current_direction_right = config.DIRECTION_R

        self.setup_ui()
        self.apply_styles()
        self.connect_signals()
        
        # Đặt chế độ ban đầu và cập nhật trạng thái các input
        self.on_mode_changed("auto")
        self.update_angle_display()

    def setup_ui(self):
        """Thiết lập giao diện."""
        main_layout = QHBoxLayout(self)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Phần bên trái - Input fields
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel)

        # Đường phân cách dọc
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setFixedWidth(2)
        separator.setStyleSheet("background-color: #FFFFFF;")
        main_layout.addWidget(separator)

        # Phần bên phải
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel)

    def create_left_panel(self):
        """Tạo panel bên trái với các input fields."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(8)

        # Title
        title = QLabel("Nhập thông số")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #F1F5F9;")
        layout.addWidget(title)

        # Input fields
        self.wind_speed_inputs = []
        self.wind_dir_inputs = []

        # Gió dọc dàn đạo
        label_text = "Gió dọc đạn đạo thấp"
        capsule = self.create_input_row(label_text, "0", "m/s", note_text="Gió thổi theo hướng đạn ở độ cao thấp (âm: xuôi chiều, dương: ngược chiều)")
        layout.addWidget(capsule)
        self.wind_speed_inputs.append(capsule)

        label_text = "Gió dọc đạn đạo cao"
        capsule = self.create_input_row(label_text, "0", "m/s", note_text="Gió thổi theo hướng đạn ở độ cao lớn (âm: xuôi chiều, dương: ngược chiều)")
        layout.addWidget(capsule)
        self.wind_speed_inputs.append(capsule)

        # Gió ngang đạn đạo
        label_text = "Gió ngang đạn đạo thấp"
        capsule = self.create_input_row(label_text, "0", "m/s", note_text="Gió thổi vuông góc với hướng đạn ở độ cao thấp (dương: phải sang trái, âm: trái sang phải)")
        layout.addWidget(capsule)
        self.wind_dir_inputs.append(capsule)

        # Gió ngang đạn đạo cao
        label_text = "Gió ngang đạn đạo cao"
        capsule = self.create_input_row(label_text, "0", "m/s", note_text="Gió thổi vuông góc với hướng đạn ở độ cao lớn (dương: phải sang trái, âm: trái sang phải)")
        layout.addWidget(capsule)
        self.wind_dir_inputs.append(capsule)

        # Mật độ không khí
        self.air_density_input = self.create_input_row("Áp suất không khí", str(self.standard_pressure), "mmHg", 
                                                        note_text="Áp suất khí quyển tại vị trí bắn")
        layout.addWidget(self.air_density_input)

        # Nhiệt độ không khí
        self.air_temp_input = self.create_input_row("Nhiệt độ không khí", str(self.standard_temp), "°C",
                                                     note_text="Nhiệt độ môi trường không khí ngoài trời")
        layout.addWidget(self.air_temp_input)

        # Nhiệt độ liều phóng
        self.charge_temp_input = self.create_input_row("Nhiệt độ liều phóng", str(self.standard_charge_temp), "°C",
                                                        note_text="Nhiệt độ của thuốc phóng trong đạn")
        layout.addWidget(self.charge_temp_input)

        # Thuốc phóng kacn-14 (chỉ nhận 0 hoặc 1)
        self.kacn_input = self.create_input_row("Thuốc phóng kacn-14", "0", "", binary_mode=True,
                                                 note_text="Loại thuốc phóng: 0 = thường, 1 = kacn-14")
        layout.addWidget(self.kacn_input)

        # Góc tạ mục tiêu
        self.target_angle_input = self.create_input_row("Góc tà mục tiêu", "0", "ly giác",
                                                         note_text="Góc chênh của mục tiêu (dương: mục tiêu cao hơn, âm: mục tiêu thấp hơn)")
        layout.addWidget(self.target_angle_input)

        layout.addStretch()

        return panel

    def create_right_panel(self):
        """Tạo panel bên phải với mode selector và bảng."""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        layout.setSpacing(15)

        # Mode selector (thay thế toggle switch)
        self.mode_selector = ModeSelector()
        self.mode_selector.on_mode_change_callback = self.on_mode_changed
        layout.addWidget(self.mode_selector)

        # Input fields cho vị trí mục tiêu (thay thế input cho từng pháo)
        self.manual_panel = QWidget()
        manual_layout = QVBoxLayout(self.manual_panel)
        manual_layout.setSpacing(8)

        # Khoảng cách từ tàu đến mục tiêu
        self.ship_to_target_distance_input = self.create_input_row(
            "Khoảng cách tàu - mục tiêu", "0", "m",
            note_text="Khoảng cách từ quang điện tử trên tàu đến mục tiêu"
        )
        manual_layout.addWidget(self.ship_to_target_distance_input)

        # Góc hướng từ tàu đến mục tiêu
        self.ship_to_target_azimuth_input = self.create_input_row(
            "Góc hướng tàu - mục tiêu", "0", "độ",
            note_text="Góc hướng từ tàu đến mục tiêu (0° = phía trước, 90° = phải, -90° = trái)"
        )
        manual_layout.addWidget(self.ship_to_target_azimuth_input)

        # Labels hiển thị khoảng cách tính được cho từng pháo (read-only)
        distance_title = QLabel("Khoảng cách tính toán cho từng pháo:")
        distance_title.setStyleSheet("font-size: 13px; font-weight: bold; color: #94A3B8; margin-top: 10px;")
        manual_layout.addWidget(distance_title)

        self.cannon_left_distance_label = self.create_readonly_display("Khoảng cách pháo trái", "0", "m")
        manual_layout.addWidget(self.cannon_left_distance_label)

        self.cannon_right_distance_label = self.create_readonly_display("Khoảng cách pháo phải", "0", "m")
        manual_layout.addWidget(self.cannon_right_distance_label)

        # Disable mặc định khi ở chế độ tự động
        self.ship_to_target_distance_input.setEnabled(False)
        self.ship_to_target_azimuth_input.setEnabled(False)


        layout.addWidget(self.manual_panel)

        # Đường phân cách
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.HLine)
        separator1.setFrameShadow(QFrame.Sunken)
        separator1.setStyleSheet("background-color: #475569;")
        layout.addWidget(separator1)

        # Bảng hiển thị góc tầm và góc hướng
        table_title = QLabel("Góc trước và sau khi áp dụng")
        table_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F1F5F9; margin-top: 5px;")
        layout.addWidget(table_title)

        table = self.create_angle_table()
        layout.addWidget(table)

        # Đường phân cách
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #475569;")
        layout.addWidget(separator)

        # Giá trị tiêu chuẩn
        standard_title = QLabel("Giá trị tiêu chuẩn")
        standard_title.setStyleSheet("font-size: 14px; font-weight: bold; color: #F1F5F9;")
        layout.addWidget(standard_title)

        standard = self.create_standard_values()
        layout.addWidget(standard)

        # Nút OK và Cancel
        buttons = self.create_buttons()
        layout.addLayout(buttons)

        return panel

    def create_input_row(self, label_text, default_value, unit, binary_mode=False, note_text=""):
        """Tạo một widget input hình viên thuốc với ghi chú.
        
        Args:
            label_text: Text hiển thị bên trái
            default_value: Giá trị mặc định
            unit: Đơn vị hiển thị bên phải
            binary_mode: Nếu True, chỉ chấp nhận 0 hoặc 1
            note_text: Text ghi chú cố định (không edit được)
        """
        # Container chứa capsule input và ghi chú (vertical layout)
        row_widget = QWidget()
        row_layout = QVBoxLayout(row_widget)
        row_layout.setContentsMargins(0, 0, 0, 0)
        row_layout.setSpacing(3)
        
        # Capsule input ở trên
        capsule_input = CapsuleInput(label_text, default_value, unit)
        
        # Nếu là binary mode, đặt validator đặc biệt
        if binary_mode:
            capsule_input.input_field.setValidator(BinaryValidator())
        
        row_layout.addWidget(capsule_input)
        
        # Label ghi chú cố định ở dưới (nếu có note_text)
        if note_text:
            note_label = QLabel(note_text)
            note_label.setFixedHeight(20)
            note_label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
            note_label.setWordWrap(True)
            note_label.setStyleSheet("""
                QLabel {
                    background-color: transparent;
                    color: #94A3B8;
                    font-size: 11px;
                    font-style: italic;
                    padding-left: 5px;
                    padding-right: 5px;
                }
            """)
            row_layout.addWidget(note_label)
            row_widget.note_label = note_label
        
        # Lưu references để có thể truy cập dễ dàng
        row_widget.capsule_input = capsule_input
        
        # Thêm helper methods để truy cập giá trị như trước
        row_widget.text = capsule_input.text
        row_widget.setText = capsule_input.setText
        row_widget.setEnabled = capsule_input.setEnabled
        
        # Expose signal từ capsule input
        row_widget.textChanged = capsule_input.textChanged
        
        return row_widget

    def create_readonly_display(self, label_text, default_value, unit):
        """Tạo một widget hiển thị read-only (không cho phép chỉnh sửa).
        
        Args:
            label_text: Text hiển thị bên trái
            default_value: Giá trị mặc định
            unit: Đơn vị hiển thị bên phải
        """
        # Tạo capsule input nhưng disabled
        capsule = CapsuleInput(label_text, default_value, unit)
        capsule.input_field.setReadOnly(True)
        capsule.setStyleSheet("""
            QLineEdit {
                background-color: #3a3a3a;
                color: #94A3B8;
                border: none;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Tahoma', Arial, sans-serif;
                padding-right: 10px;
            }
        """)
        return capsule

    def create_angle_table(self):
        """Tạo bảng hiển thị góc tầm và góc hướng."""
        table = QWidget()
        layout = QGridLayout(table)
        layout.setSpacing(1)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header chính (hàng 0) - span 2 cột cho mỗi tiêu đề
        header_label_empty = QLabel("")
        header_label_empty.setAlignment(Qt.AlignCenter)
        header_label_empty.setStyleSheet("""
            background-color: #334155;
            color: #F1F5F9;
            font-weight: bold;
            font-size: 13px;
            padding: 10px;
            border: 1px solid #475569;
        """)
        layout.addWidget(header_label_empty, 0, 0, 2, 1)  # Span 2 hàng

        # "Góc tầm" span 2 cột
        header_elevation = QLabel("Góc tầm")
        header_elevation.setAlignment(Qt.AlignCenter)
        header_elevation.setStyleSheet("""
            background-color: #334155;
            color: #F1F5F9;
            font-weight: bold;
            font-size: 13px;
            padding: 10px;
            border: 1px solid #475569;
        """)
        layout.addWidget(header_elevation, 0, 1, 1, 2)  # Span 2 cột

        # "Góc hướng" span 2 cột
        header_direction = QLabel("Góc hướng")
        header_direction.setAlignment(Qt.AlignCenter)
        header_direction.setStyleSheet("""
            background-color: #334155;
            color: #F1F5F9;
            font-weight: bold;
            font-size: 13px;
            padding: 10px;
            border: 1px solid #475569;
        """)
        layout.addWidget(header_direction, 0, 3, 1, 2)  # Span 2 cột

        # Sub-headers (hàng 1) - Trái/Phải cho mỗi nhóm
        sub_headers = ["Trái", "Phải", "Trái", "Phải"]
        for col, sub_header in enumerate(sub_headers, 1):
            label = QLabel(sub_header)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                background-color: #475569;
                color: #F1F5F9;
                font-weight: bold;
                font-size: 12px;
                padding: 8px;
                border: 1px solid #475569;
            """)
            layout.addWidget(label, 1, col)

        # Rows - Mặc định và Áp dụng lượng sửa
        row_labels = ["Mặc định", "Áp dụng lượng sửa"]
        self.angle_cells = {}

        for row, row_label in enumerate(row_labels, 2):  # Bắt đầu từ hàng 2
            # Row label
            label = QLabel(row_label)
            label.setAlignment(Qt.AlignCenter)
            label.setStyleSheet("""
                background-color: #334155;
                color: #F1F5F9;
                font-size: 13px;
                padding: 10px;
                border: 1px solid #475569;
            """)
            layout.addWidget(label, row, 0)

            # Cells: 4 cột (Góc tầm Trái, Góc tầm Phải, Góc hướng Trái, Góc hướng Phải)
            cell_keys = [
                ('elevation_left', 1),
                ('elevation_right', 2),
                ('direction_left', 3),
                ('direction_right', 4)
            ]

            for key_suffix, col in cell_keys:
                cell_label = QLabel("0.0°")
                cell_label.setAlignment(Qt.AlignCenter)
                cell_label.setStyleSheet("""
                    background-color: #1E293B;
                    color: #F1F5F9;
                    font-size: 14px;
                    padding: 10px;
                    border: 1px solid #475569;
                """)
                layout.addWidget(cell_label, row, col)

                # Lưu reference để update sau
                key = f"{'default' if row == 2 else 'corrected'}_{key_suffix}"
                self.angle_cells[key] = cell_label

        return table

    def create_standard_values(self):
        """Tạo widget hiển thị giá trị tiêu chuẩn."""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)

        # Nhiệt độ không khí tiêu chuẩn
        self.std_temp_input = self.create_input_row("Nhiệt độ không khí tiêu chuẩn", str(self.standard_temp), "°C")
        layout.addWidget(self.std_temp_input)

        # Áp suất khí quyển tiêu chuẩn
        self.std_pressure_input = self.create_input_row("Áp suất khí quyển tiêu chuẩn", str(self.standard_pressure), "mmHg")
        layout.addWidget(self.std_pressure_input)

        # Nhiệt độ liều phóng tiêu chuẩn
        self.std_charge_temp_input = self.create_input_row("Nhiệt độ liều phóng tiêu chuẩn", str(self.standard_charge_temp), "°C")
        layout.addWidget(self.std_charge_temp_input)

        return widget

    def create_buttons(self):
        """Tạo nút Reset, OK và Cancel."""
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        # Reset Button (bên trái)
        self.reset_btn = QPushButton("↻")
        self.reset_btn.setFixedSize(40, 40)
        self.reset_btn.setCursor(Qt.PointingHandCursor)
        self.reset_btn.clicked.connect(self.on_reset_clicked)
        self.reset_btn.setStyleSheet("""
            QPushButton {
                background-color: #6B7280;
                color: #F1F5F9;
                border: none;
                border-radius: 20px;
                font-size: 24px;
                font-weight: bold;
                font-family: 'Tahoma', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #4B5563;
            }
            QPushButton:pressed {
                background-color: #374151;
            }
        """)
        button_layout.addWidget(self.reset_btn)
        
        button_layout.addStretch()

        # OK Button (checkmark icon)
        self.ok_btn = QPushButton("✓")
        self.ok_btn.setFixedSize(40, 40)
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.clicked.connect(self.on_ok_clicked)
        self.ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: #F1F5F9;
                border: none;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Tahoma', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        button_layout.addWidget(self.ok_btn)

        # Cancel Button (X icon)
        self.cancel_btn = QPushButton("✕")
        self.cancel_btn.setFixedSize(40, 40)
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn.clicked.connect(self.on_cancel_clicked)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: #F1F5F9;
                border: none;
                border-radius: 20px;
                font-size: 20px;
                font-weight: bold;
                font-family: 'Tahoma', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
            QPushButton:pressed {
                background-color: #991B1B;
            }
        """)
        button_layout.addWidget(self.cancel_btn)

        return button_layout

    def on_ok_clicked(self):
        """Xử lý khi nhấn OK - áp dụng lượng sửa."""
        corrections = self.get_corrections()

        # KHÔNG cập nhật config - chỉ gửi lượng sửa để UI hiển thị
        # Gọi callback nếu có (để cập nhật UI với lượng sửa)
        if hasattr(self, 'on_angles_updated') and callable(self.on_angles_updated):
            self.on_angles_updated(corrections)

        # Lấy góc MỤC TIÊU từ config (góc từ nội suy bảng bắn)
        aim_elevation_left = config.AIM_ANGLE_L
        aim_elevation_right = config.AIM_ANGLE_R
        aim_direction_left = config.AIM_DIRECTION_L
        aim_direction_right = config.AIM_DIRECTION_R
        
        # Nếu chưa có góc hướng mục tiêu (chưa nhập tọa độ), sử dụng góc hướng hiện tại từ cảm biến
        if aim_direction_left == 0:
            aim_direction_left = config.DIRECTION_L
        if aim_direction_right == 0:
            aim_direction_right = config.DIRECTION_R
        
        # Tính góc đã được điều chỉnh = góc mục tiêu + lượng sửa
        elevation_left = aim_elevation_left + corrections['elevation_correction_left']
        direction_left = aim_direction_left + corrections['direction_correction_left']
        elevation_left_int = int(elevation_left * 10)  # Chuyển sang số nguyên * 10
        direction_left_int = int(direction_left * 10)  # Chuyển sang số nguyên * 10
        
        # Tạo CAN data cho giàn trái
        idx_left = 0x01A
        can_data_left = [
            idx_left,
            elevation_left_int & 0xFF,
            (elevation_left_int >> 8) & 0xFF,
            direction_left_int & 0xFF,
            (direction_left_int >> 8) & 0xFF,
            0x11
        ]
        can_data_hex_left = ' '.join([f'0x{byte:02X}' for byte in can_data_left])
        can_data_explained_left = (
            f"[Giàn: Trái (0x{idx_left:02X}), "
            f"Góc tầm: {elevation_left:.1f}° (0x{elevation_left_int:04X}), "
            f"Góc hướng: {direction_left:.1f}° (0x{direction_left_int:04X}), "
            f"Lệnh: 0x{can_data_left[5]:02X}]"
        )
        
        # Gửi lệnh cho giàn trái
        if sender_angle_direction(elevation_left_int, direction_left_int, idx=idx_left):
            from ui.views.event_log_tab import LogTab
            LogTab.log(f"Đã gửi lệnh góc tầm {elevation_left:.1f}° và góc hướng {direction_left:.1f}° cho giàn Trái - CAN Data: [{can_data_hex_left}]", "SUCCESS")
        else:
            from ui.views.event_log_tab import LogTab
            LogTab.log(f"Không thể gửi lệnh góc qua CAN bus cho giàn Trái - CAN Data: [{can_data_hex_left}] - ID: 0x29", "ERROR")
            LogTab.log(f"Chi tiết CAN Data: {can_data_explained_left}", "ERROR")
        
        # Gửi CAN message cho giàn phải (idx=0x32)
        elevation_right = aim_elevation_right + corrections['elevation_correction_right']
        direction_right = aim_direction_right + corrections['direction_correction_right']
        elevation_right_int = int(elevation_right * 10)  # Chuyển sang số nguyên * 10
        direction_right_int = int(direction_right * 10)  # Chuyển sang số nguyên * 10
        
        # Tạo CAN data cho giàn phải
        idx_right = 0x01B
        can_data_right = [
            idx_right,
            elevation_right_int & 0xFF,
            (elevation_right_int >> 8) & 0xFF,
            direction_right_int & 0xFF,
            (direction_right_int >> 8) & 0xFF,
            0x11
        ]
        can_data_hex_right = ' '.join([f'0x{byte:02X}' for byte in can_data_right])
        can_data_explained_right = (
            f"[Giàn: Phải (0x{idx_right:02X}), "
            f"Góc tầm: {elevation_right:.1f}° (0x{elevation_right_int:04X}), "
            f"Góc hướng: {direction_right:.1f}° (0x{direction_right_int:04X}), "
            f"Lệnh: 0x{can_data_right[5]:02X}]"
        )
        
        # Gửi lệnh cho giàn phải
        if sender_angle_direction(elevation_right_int, direction_right_int, idx=idx_right):
            from ui.views.event_log_tab import LogTab
            LogTab.log(f"Đã gửi lệnh góc tầm {elevation_right:.1f}° và góc hướng {direction_right:.1f}° cho giàn Phải - CAN Data: [{can_data_hex_right}]", "SUCCESS")
        else:
            from ui.views.event_log_tab import LogTab
            LogTab.log(f"Không thể gửi lệnh góc qua CAN bus cho giàn Phải - CAN Data: [{can_data_hex_right}] - ID: 0x29", "ERROR")
            LogTab.log(f"Chi tiết CAN Data: {can_data_explained_right}", "ERROR")

        # Ẩn widget
        self.hide()

    def on_cancel_clicked(self):
        """Xử lý khi nhấn Cancel - đóng mà không áp dụng."""
        self.hide()

    def on_reset_clicked(self):
        """Xử lý khi nhấn Reset - reset tất cả các input về giá trị mặc định."""
        # Reset các input gió về 0 (các input này mặc định là 0)
        for input_field in self.wind_speed_inputs + self.wind_dir_inputs:
            input_field.setText("0")
        
        # Reset áp suất, nhiệt độ về giá trị tiêu chuẩn (KHÔNG phải 0)
        self.air_density_input.setText(str(self.standard_pressure))  # 750 mmHg
        self.air_temp_input.setText(str(self.standard_temp))  # 15.9 °C
        self.charge_temp_input.setText(str(self.standard_charge_temp))  # 15 °C
        
        # Reset thuốc phóng kacn-14 và góc tạ về 0
        self.kacn_input.setText("0")
        self.target_angle_input.setText("0")
        
        # Reset các input vị trí mục tiêu về 0
        self.ship_to_target_distance_input.setText("0")
        self.ship_to_target_azimuth_input.setText("0")
        
        # Đảm bảo giá trị tiêu chuẩn không thay đổi
        self.std_temp_input.setText(str(self.standard_temp))
        self.std_pressure_input.setText(str(self.standard_pressure))
        self.std_charge_temp_input.setText(str(self.standard_charge_temp))
        
        # Reset về chế độ tự động nếu đang ở chế độ thủ công
        # if not self.toggle_switch.is_auto:
        #     self.toggle_switch.is_auto = True
        #     self.toggle_switch.update()
        #     self.on_mode_changed(True)
        
        # Cập nhật lại hiển thị
        self.update_angle_display()

    def connect_signals(self):
        """Kết nối các signals để tự động cập nhật khi input thay đổi."""
        # Kết nối tất cả các input fields để tự động cập nhật
        for input_field in self.wind_speed_inputs + self.wind_dir_inputs:
            input_field.textChanged.connect(self.update_angle_display)

        self.air_density_input.textChanged.connect(self.update_angle_display)
        self.air_temp_input.textChanged.connect(self.update_angle_display)
        self.charge_temp_input.textChanged.connect(self.update_angle_display)
        self.kacn_input.textChanged.connect(self.update_angle_display)
        self.target_angle_input.textChanged.connect(self.update_angle_display)

        # Kết nối input fields cho vị trí mục tiêu
        self.ship_to_target_distance_input.textChanged.connect(self.on_target_position_changed)
        self.ship_to_target_azimuth_input.textChanged.connect(self.on_target_position_changed)

        # Kết nối giá trị tiêu chuẩn
        self.std_temp_input.textChanged.connect(self.update_angle_display)
        self.std_pressure_input.textChanged.connect(self.update_angle_display)
        self.std_charge_temp_input.textChanged.connect(self.update_angle_display)

    def on_mode_changed(self, mode:str):
        """Xử lý khi chuyển đổi giữa 3 chế độ: tự động, bán tự động, thủ công.
        
        Args:
            mode: "auto", "semi-auto", hoặc "manual"
        """
        is_auto = (mode == "auto")
        is_semi_auto = (mode == "semi-auto")
        is_manual = (mode == "manual")
        
        # Enable/disable các input vị trí mục tiêu
        # - Tự động: disable (lấy từ CAN bus)
        # - Bán tự động: enable (cho phép nhập)
        # - Thủ công: enable (nhập hoàn toàn thủ công)
        enable_manual_inputs = is_semi_auto or is_manual
        self.ship_to_target_distance_input.setEnabled(enable_manual_inputs)
        self.ship_to_target_azimuth_input.setEnabled(enable_manual_inputs)

        # Enable/disable các input bên trái (điều kiện môi trường)
        # - Tự động: enable (sử dụng để tính toán)
        # - Bán tự động: enable (tham khảo, nhưng có thể sửa thủ công)
        # - Thủ công: disable (không dùng đến, nhập trực tiếp lượng sửa)
        enable_env_inputs = is_auto or is_semi_auto
        for input_field in self.wind_speed_inputs + self.wind_dir_inputs:
            input_field.setEnabled(enable_env_inputs)

        self.air_density_input.setEnabled(enable_env_inputs)
        self.air_temp_input.setEnabled(enable_env_inputs)
        self.charge_temp_input.setEnabled(enable_env_inputs)
        self.kacn_input.setEnabled(enable_env_inputs)
        self.target_angle_input.setEnabled(enable_env_inputs)

        # Cập nhật lại góc khi chuyển mode
        self.update_angle_display()

    def on_target_position_changed(self):
        """Xử lý khi vị trí mục tiêu thay đổi - tính khoảng cách từ từng pháo đến mục tiêu."""
        try:
            # Lấy khoảng cách và góc hướng từ tàu đến mục tiêu
            distance_ship_to_target = float(self.ship_to_target_distance_input.text() or 0)
            azimuth_ship_to_target = float(self.ship_to_target_azimuth_input.text() or 0)
            
            # Import các class cần thiết từ data_receiver
            from communication.data_receiver import Ship, Point2D
            import math
            
            # Tạo ship với kích thước chuẩn
            ship = Ship()
            
            # Tính vị trí mục tiêu dựa trên vị trí quang điện tử
            optoelectronic_pos = ship.get_optoelectronic()
            azimuth_rad = math.radians(azimuth_ship_to_target)
            
            target_x = optoelectronic_pos.x + distance_ship_to_target * math.sin(azimuth_rad)
            target_y = optoelectronic_pos.y + distance_ship_to_target * math.cos(azimuth_rad)
            target_position = Point2D(target_x, target_y)
            
            # Tính khoảng cách từ mỗi pháo đến mục tiêu
            cannons = ship.get_cannons()
            cannon_left_pos = cannons[0][1]  # cannon_1
            cannon_right_pos = cannons[1][1]  # cannon_2
            
            distance_left = cannon_left_pos.distance(target_position)
            distance_right = cannon_right_pos.distance(target_position)
            
            # Cập nhật hiển thị khoảng cách
            self.cannon_left_distance_label.setText(f"{distance_left:.2f}")
            self.cannon_right_distance_label.setText(f"{distance_right:.2f}")
            
            # Cập nhật config (để tính toán lượng sửa)
            config.DISTANCE_L = distance_left
            config.DISTANCE_R = distance_right
            
            # Cập nhật góc hướng cho từng pháo
            delta_x_left = target_x - cannon_left_pos.x
            delta_y_left = target_y - cannon_left_pos.y
            azimuth_left_rad = math.atan2(delta_x_left, delta_y_left)
            azimuth_left_deg = math.degrees(azimuth_left_rad)
            
            delta_x_right = target_x - cannon_right_pos.x
            delta_y_right = target_y - cannon_right_pos.y
            azimuth_right_rad = math.atan2(delta_x_right, delta_y_right)
            azimuth_right_deg = math.degrees(azimuth_right_rad)
            
            config.AIM_DIRECTION_L = azimuth_left_deg
            config.AIM_DIRECTION_R = azimuth_right_deg
            
            # Nội suy góc tầm từ bảng bắn dựa trên khoảng cách
            from common.utils import get_firing_table_interpolator
            interpolator = get_firing_table_interpolator()
            if interpolator:
                # Tính góc tầm cho pháo trái
                elevation_left = interpolator.interpolate_angle(distance_left)
                config.AIM_ANGLE_L = elevation_left
                
                # Tính góc tầm cho pháo phải
                elevation_right = interpolator.interpolate_angle(distance_right)
                config.AIM_ANGLE_R = elevation_right
            
            # Cập nhật hiển thị bảng
            self.update_angle_display()
            
        except (ValueError, AttributeError) as e:
            print(f"Lỗi tính toán khoảng cách pháo: {e}")
            self.cannon_left_distance_label.setText("0.00")
            self.cannon_right_distance_label.setText("0.00")

    def calculate_corrections(self):
        """Tính toán lượng sửa dựa trên các thông số cho cả trái và phải.
        
        CÔNG THỨC GIẢ - CẦN CHỈNH SỬA LẠI THEO YÊU CẦU THỰC TẾ
        
        Returns:
            tuple: (elev_left_corr, elev_right_corr, dir_left_corr, dir_right_corr)
        """
        # Kiểm tra chế độ hiện tại
        current_mode = self.mode_selector.get_mode()
        
        # Nếu đang ở chế độ thủ công, không tính toán lượng sửa (trả về 0)
        if current_mode == "manual":
            return 0, 0, 0, 0
        
        from common.utils import get_firing_table_interpolator, get_slope_correction_table
        
        try:
            # ========== LẤY INPUT TỪ CỘT BÊN TRÁI ==========
            # Gió
            wind_along_low = float(self.wind_speed_inputs[0].text() or 0)    # Gió dọc thấp (m/s)
            wind_along_high = float(self.wind_speed_inputs[1].text() or 0)   # Gió dọc cao (m/s)
            wind_cross_low = float(self.wind_dir_inputs[0].text() or 0)      # Gió ngang thấp (m/s)
            wind_cross_high = float(self.wind_dir_inputs[1].text() or 0)     # Gió ngang cao (m/s)
            
            # Môi trường
            air_pressure = float(self.air_density_input.text() or 0)         # Áp suất (mmHg)
            air_temp = float(self.air_temp_input.text() or 0)                # Nhiệt độ không khí (°C)
            charge_temp = float(self.charge_temp_input.text() or 0)          # Nhiệt độ liều phóng (°C)
            
            # Đạn và góc tà
            kacn14 = int(self.kacn_input.text() or 0)                        # Thuốc phóng kacn-14 (0 hoặc 1)
            slope_angle = float(self.target_angle_input.text() or 0)         # Góc tà mục tiêu (độ)
            
            # Giá trị tiêu chuẩn
            std_temp = float(self.std_temp_input.text() or self.standard_temp)
            std_pressure = float(self.std_pressure_input.text() or self.standard_pressure)
            std_charge_temp = float(self.std_charge_temp_input.text() or self.standard_charge_temp)
            
            # ========== LẤY DỮ LIỆU TỪ TABLE1 THEO KHOẢNG CÁCH ==========
            interpolator = get_firing_table_interpolator()
            if not interpolator:
                return 0, 0, 0, 0
            
            # Khoảng cách từ config
            X_left = config.DISTANCE_L   # Khoảng cách trái (m)
            X_right = config.DISTANCE_R  # Khoảng cách phải (m)
            
            # Nội suy các giá trị từ table1 cho TRÁI
            Z_left = interpolator.interpolate_z(X_left) if interpolator.z_data is not None else 0
            delta_Zwhz_left = interpolator.interpolate_delta_zwhz(X_left)
            delta_Zwbez_left = interpolator.interpolate_delta_zwbez(X_left)
            delta_Zwhx_left = interpolator.interpolate_delta_zwhx(X_left)
            delta_Xwhx_left = interpolator.interpolate_delta_xwhx(X_left)
            delta_Xwhz_left = interpolator.interpolate_delta_xwhz(X_left)
            delta_Xwbex_left = interpolator.interpolate_delta_xwbex(X_left)
            delta_Xkacn_left = interpolator.interpolate_delta_xkacn(X_left)
            delta_XH_left = interpolator.interpolate_delta_xh(X_left)
            delta_XT_left = interpolator.interpolate_delta_xt(X_left)
            delta_XTsz_left = interpolator.interpolate_delta_xtsz(X_left)
            delta_XTbic_left = interpolator.interpolate_delta_xtbic(X_left)
            
            # Nội suy các giá trị từ table1 cho PHẢI
            Z_right = interpolator.interpolate_z(X_right) if interpolator.z_data is not None else 0
            delta_Zwhz_right = interpolator.interpolate_delta_zwhz(X_right)
            delta_Zwbez_right = interpolator.interpolate_delta_zwbez(X_right)
            delta_Zwhx_right = interpolator.interpolate_delta_zwhx(X_right)
            delta_Xwhx_right = interpolator.interpolate_delta_xwhx(X_right)
            delta_Xwhz_right = interpolator.interpolate_delta_xwhz(X_right)
            delta_Xwbex_right = interpolator.interpolate_delta_xwbex(X_right)
            delta_Xkacn_right = interpolator.interpolate_delta_xkacn(X_right)
            delta_XH_right = interpolator.interpolate_delta_xh(X_right)
            delta_XT_right = interpolator.interpolate_delta_xt(X_right)
            delta_XTsz_right = interpolator.interpolate_delta_xtsz(X_right)
            delta_XTbic_right = interpolator.interpolate_delta_xtbic(X_right)
            
            # ========== CÔNG THỨC GIẢ TÍNH LƯỢNG SỬA GÓC TẦM (TRÁI) ==========
            # TODO: CHỈNH SỬA CÔNG THỨC NÀY THEO YÊU CẦU THỰC TẾ
            elev_correction_left_mils = (
                # Ảnh hưởng nhiệt độ
                delta_XT_left * (air_temp - std_temp)*0.1 +
                delta_XTsz_left * (charge_temp - std_charge_temp)*0.1 +
                
                # Ảnh hưởng áp suất/độ cao
                delta_XH_left * (air_pressure - std_pressure) * 0.1 +
                
                # Ảnh hưởng gió dọc
                delta_Xwhx_left * wind_along_low * 0.1 +
                delta_Xwbex_left * wind_along_high * 0.1 +
                
                # Ảnh hưởng gió ngang lên góc tầm
                delta_Xwhz_left * wind_cross_low * 0.1 +
                
                # Ảnh hưởng thuốc phóng kacn-14
                delta_Xkacn_left * kacn14
            ) / delta_XTbic_left if delta_XTbic_left !=0 else 0
            
            # ========== CÔNG THỨC GIẢ TÍNH LƯỢNG SỬA GÓC TẦM (PHẢI) ==========
            # TODO: CHỈNH SỬA CÔNG THỨC NÀY THEO YÊU CẦU THỰC TẾ
            elev_correction_right_mils = (
                # Ảnh hưởng nhiệt độ
                delta_XT_right * (air_temp - std_temp) * 0.1 +
                delta_XTsz_right * (charge_temp - std_charge_temp) * 0.1 +

                # Ảnh hưởng áp suất/độ cao
                delta_XH_right * (air_pressure - std_pressure) * 0.1 +
                
                # Ảnh hưởng gió dọc
                delta_Xwhx_right * wind_along_low * 0.1 +
                delta_Xwbex_right * wind_along_high * 0.1 +
                
                # Ảnh hưởng gió ngang lên góc tầm
                delta_Xwhz_right * wind_cross_low * 0.1 +

                # Ảnh hưởng thuốc phóng kacn-14
                delta_Xkacn_right * kacn14
            ) / delta_XTbic_right if delta_XTbic_right != 0 else 0
            
            # ========== CÔNG THỨC GIẢ TÍNH LƯỢNG SỬA GÓC HƯỚNG (TRÁI) ==========
            # TODO: CHỈNH SỬA CÔNG THỨC NÀY THEO YÊU CẦU THỰC TẾ
            dir_correction_left_mils = (
                # Ảnh hưởng gió ngang lên góc hướng
                delta_Zwhz_left * wind_cross_low * 0.1 +
                delta_Zwhx_left * wind_along_low * 0.1 +
                delta_Zwbez_left * wind_cross_high * 0.1
            )
            
            # ========== CÔNG THỨC GIẢ TÍNH LƯỢNG SỬA GÓC HƯỚNG (PHẢI) ==========
            # TODO: CHỈNH SỬA CÔNG THỨC NÀY THEO YÊU CẦU THỰC TẾ
            dir_correction_right_mils = (
                # Ảnh hưởng gió ngang lên góc hướng
                delta_Zwhz_right * wind_cross_low * 0.1 +
                delta_Zwhx_right * wind_along_low * 0.1 +
                delta_Zwbez_right * wind_cross_high * 0.1
            )
            
            # ========== THÊM LƯỢNG SỬA CHÊNH TÀ TỪ TABLE2 (NẾU CÓ) ==========
            if slope_angle != 0:
                slope_table = get_slope_correction_table()
                if slope_table:
                    # Lấy ly giác hiện tại từ góc tầm mục tiêu
                    current_elev_mils_left = config.AIM_ANGLE_L / 0.05625  # Chuyển độ về ly giác
                    current_elev_mils_right = config.AIM_ANGLE_R / 0.05625
                    
                    # Tra bảng table2
                    try:
                        p_correction_left_mils = slope_table.lookup(slope_angle, current_elev_mils_left)
                        p_correction_right_mils = slope_table.lookup(slope_angle, current_elev_mils_right)
                        
                        # Cộng thêm vào lượng sửa góc tầm
                        elev_correction_left_mils += p_correction_left_mils
                        elev_correction_right_mils += p_correction_right_mils
                    except Exception as e:
                        print(f"Lỗi tra bảng chênh tà: {e}")
            
            # ========== CHUYỂN ĐỔI TỪ LY GIÁC SANG ĐỘ ==========
            elev_left_corr = elev_correction_left_mils * 0.05625
            elev_right_corr = elev_correction_right_mils * 0.05625
            dir_left_corr = dir_correction_left_mils * 0.05625
            dir_right_corr = dir_correction_right_mils * 0.05625
            
            return elev_left_corr, elev_right_corr, dir_left_corr, dir_right_corr

        except Exception as e:
            print(f"Lỗi tính toán lượng sửa: {e}")
            return 0, 0, 0, 0

    def update_angle_display(self):
        """Cập nhật hiển thị góc tầm và góc hướng."""
        # ĐỌC TRỰC TIẾP từ config
        # Góc MỤC TIÊU (từ nội suy bảng bắn) - đây là góc cơ sở để áp dụng lượng sửa
        aim_elevation_left = config.AIM_ANGLE_L
        aim_elevation_right = config.AIM_ANGLE_R
        aim_direction_left = config.AIM_DIRECTION_L
        aim_direction_right = config.AIM_DIRECTION_R
        
        current_mode = self.mode_selector.get_mode()
        
        if current_mode == "auto":
            # Chế độ tự động - tính toán lượng sửa cho cả trái và phải
            elev_left_corr, elev_right_corr, dir_left_corr, dir_right_corr = self.calculate_corrections()

            # Hiển thị góc mặc định (góc mục tiêu từ nội suy) - cả trái và phải
            self.angle_cells['default_elevation_left'].setText(f"{aim_elevation_left:.1f}°")
            self.angle_cells['default_elevation_right'].setText(f"{aim_elevation_right:.1f}°")
            self.angle_cells['default_direction_left'].setText(f"{aim_direction_left:.1f}°")
            self.angle_cells['default_direction_right'].setText(f"{aim_direction_right:.1f}°")

            # Hiển thị góc sau khi áp dụng lượng sửa (góc mục tiêu + lượng sửa)
            corrected_elevation_left = aim_elevation_left + elev_left_corr
            corrected_elevation_right = aim_elevation_right + elev_right_corr
            corrected_direction_left = aim_direction_left + dir_left_corr
            corrected_direction_right = aim_direction_right + dir_right_corr

            self.angle_cells['corrected_elevation_left'].setText(f"{corrected_elevation_left:.1f}°")
            self.angle_cells['corrected_elevation_right'].setText(f"{corrected_elevation_right:.1f}°")
            self.angle_cells['corrected_direction_left'].setText(f"{corrected_direction_left:.1f}°")
            self.angle_cells['corrected_direction_right'].setText(f"{corrected_direction_right:.1f}°")

        elif current_mode == "semi-auto" or current_mode == "manual":
            # Chế độ bán tự động hoặc thủ công - tính toán dựa trên vị trí mục tiêu nhập tay
            elev_left_corr, elev_right_corr, dir_left_corr, dir_right_corr = self.calculate_corrections()
            
            # Hiển thị góc mặc định
            self.angle_cells['default_elevation_left'].setText(f"{aim_elevation_left:.1f}°")
            self.angle_cells['default_elevation_right'].setText(f"{aim_elevation_right:.1f}°")
            self.angle_cells['default_direction_left'].setText(f"{aim_direction_left:.1f}°")
            self.angle_cells['default_direction_right'].setText(f"{aim_direction_right:.1f}°")

            # Hiển thị góc sau khi áp dụng lượng sửa
            corrected_elevation_left = aim_elevation_left + elev_left_corr
            corrected_elevation_right = aim_elevation_right + elev_right_corr
            corrected_direction_left = aim_direction_left + dir_left_corr
            corrected_direction_right = aim_direction_right + dir_right_corr

            self.angle_cells['corrected_elevation_left'].setText(f"{corrected_elevation_left:.1f}°")
            self.angle_cells['corrected_elevation_right'].setText(f"{corrected_elevation_right:.1f}°")
            self.angle_cells['corrected_direction_left'].setText(f"{corrected_direction_left:.1f}°")
            self.angle_cells['corrected_direction_right'].setText(f"{corrected_direction_right:.1f}°")

    def get_corrections(self):
        """Lấy lượng sửa (không bao gồm góc gốc) - đã chuyển đổi sang độ."""
        # Tất cả các chế độ đều dùng calculate_corrections()
        elev_left_corr, elev_right_corr, dir_left_corr, dir_right_corr = self.calculate_corrections()
        
        return {
            'elevation_correction_left': elev_left_corr,
            'elevation_correction_right': elev_right_corr,
            'direction_correction_left': dir_left_corr,
            'direction_correction_right': dir_right_corr
        }

    def get_corrected_angles(self):
        """Lấy góc đã được điều chỉnh (góc gốc + lượng sửa)."""
        # ĐỌC TRỰC TIẾP từ config để luôn có giá trị mới nhất từ cảm biến
        current_elevation_left = config.ANGLE_L
        current_elevation_right = config.ANGLE_R
        current_direction_left = config.DIRECTION_L
        current_direction_right = config.DIRECTION_R
        
        corrections = self.get_corrections()

        return {
            'elevation_left': current_elevation_left + corrections['elevation_correction_left'],
            'elevation_right': current_elevation_right + corrections['elevation_correction_right'],
            'direction_left': current_direction_left + corrections['direction_correction_left'],
            'direction_right': current_direction_right + corrections['direction_correction_right'],
            'elevation_correction_left': corrections['elevation_correction_left'],
            'elevation_correction_right': corrections['elevation_correction_right'],
            'direction_correction_left': corrections['direction_correction_left'],
            'direction_correction_right': corrections['direction_correction_right']
        }

    def apply_styles(self):
        """Áp dụng stylesheet chung cho widget."""
        # Chỉ áp dụng cho widget chính (dùng ID selector)
        self.setStyleSheet("""
            #ballistic_calculator_main {
                background-color: #000000;
                border: 3px solid #FFFFFF;
            }
        """)
