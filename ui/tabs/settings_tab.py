from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QColorDialog, QSpinBox, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt5.QtCore import Qt, QRectF, QTimer, QPointF, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QRadialGradient
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
import yaml
import math
import os
from common.utils import resource_path

class RippleButton(QtWidgets.QPushButton):
    """Custom QPushButton với hiệu ứng Ripple (sóng lan) như Material Design."""
    
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.ripple_color = QColor(255, 255, 255, 100)  # Màu trắng với độ trong suốt
        self.ripple_radius = 0
        self.ripple_center = QPointF()
        self.ripple_animation = QPropertyAnimation(self, b"ripple_radius", self)
        self.ripple_animation.setDuration(600)  # Thời gian hiệu ứng 600ms
        self.ripple_animation.setEasingCurve(QEasingCurve.OutCubic)
        self.ripple_animation.finished.connect(self._on_ripple_finished)
        self.max_ripple_radius = 0
        self.show_ripple = False
        
    def set_ripple_color(self, color):
        """Thiết lập màu sắc cho hiệu ứng ripple."""
        self.ripple_color = color
        
    @QtCore.pyqtProperty(float)
    def ripple_radius(self):
        return self._ripple_radius
    
    @ripple_radius.setter
    def ripple_radius(self, value):
        self._ripple_radius = value
        self.update()  # Trigger repaint
        
    def mousePressEvent(self, event):
        """Xử lý sự kiện nhấn chuột để bắt đầu hiệu ứng ripple."""
        if self.isEnabled():
            # Tính toán tâm của hiệu ứng ripple tại điểm nhấn
            self.ripple_center = event.pos()
            
            # Tính bán kính tối đa (đường chéo của nút)
            rect = self.rect()
            self.max_ripple_radius = (rect.width() ** 2 + rect.height() ** 2) ** 0.5
            
            # Bắt đầu hiệu ứng
            self.show_ripple = True
            self.ripple_animation.setStartValue(0)
            self.ripple_animation.setEndValue(self.max_ripple_radius * 1.5)  # Mở rộng hơn một chút
            self.ripple_animation.start()
            
        super().mousePressEvent(event)
        
    def _on_ripple_finished(self):
        """Được gọi khi hiệu ứng ripple hoàn thành."""
        self.show_ripple = False
        self.update()
        
    def paintEvent(self, event):
        """Vẽ nút với hiệu ứng ripple."""
        # Vẽ nút mặc định trước (bao gồm text và style)
        super().paintEvent(event)
        
        # Vẽ hiệu ứng ripple nếu đang hiển thị
        if self.show_ripple and self.ripple_radius > 0:
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            
            # Tạo gradient cho hiệu ứng ripple
            gradient = QRadialGradient(self.ripple_center, self.ripple_radius)
            
            # Đảm bảo ripple_color là QColor object
            if isinstance(self.ripple_color, QColor):
                ripple_color = self.ripple_color
            else:
                ripple_color = QColor(self.ripple_color)
            
            # Tạo màu với alpha là int
            alpha_center = 0
            alpha_mid = int(ripple_color.alpha() * 0.8)  # Chuyển float thành int
            alpha_edge = 0
            
            # Gradient từ trong suốt ở tâm đến màu ripple ở biên
            gradient.setColorAt(0, QColor(ripple_color.red(), ripple_color.green(), ripple_color.blue(), alpha_center))  # Trong suốt ở tâm
            gradient.setColorAt(0.7, QColor(ripple_color.red(), ripple_color.green(), ripple_color.blue(), alpha_mid))  # Màu ripple mạnh
            gradient.setColorAt(1, QColor(ripple_color.red(), ripple_color.green(), ripple_color.blue(), alpha_edge))  # Trong suốt ở biên
            
            painter.setBrush(QBrush(gradient))
            
            # Vẽ vòng tròn ripple
            ripple_rect = QRectF(
                self.ripple_center.x() - self.ripple_radius,
                self.ripple_center.y() - self.ripple_radius,
                self.ripple_radius * 2,
                self.ripple_radius * 2
            )
            painter.drawEllipse(ripple_rect)

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

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QColorDialog, QSpinBox, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox, QScrollArea, QSizePolicy, QSpacerItem, QFrame, QLineEdit
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
import yaml
import os
from common.utils import resource_path

class SettingTab(GridBackgroundWidget):
    def __init__(self, config_data, parent=None):
        super().__init__(parent, enable_animation=config_data['MainWindow'].get('background_animation', True))
        self.config = config_data.copy()  # Work with a copy to avoid modifying original until saved
        self.main_tab = None  # Will be set by parent
        self.setupUi()

    # ...existing code...

    def setupUi(self):
        # Create main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)  # Giảm spacing từ 20 xuống 15

        # Spacer để tách biệt title và config
        spacer = QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Fixed)
        main_layout.addItem(spacer)

        # Create scroll area for config section
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setStyleSheet("border: none; background: transparent;")

        # Create container widget for scroll area
        scroll_widget = QtWidgets.QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(0, 0, 0, 0)

        # Create horizontal layout for group boxes inside scroll area
        groups_layout = QHBoxLayout()
        groups_layout.setSpacing(15)

        # Create group boxes for each state
        self.color_buttons = {}  # Store color buttons for each state and key
        self.alpha_spins = {}    # Store alpha spin boxes

        # Create group boxes
        enabled_group = self.create_color_group_widget("Có thể bấm", "enabled")
        disabled_group = self.create_color_group_widget("Không thể bấm", "disabled")
        selected_group = self.create_color_group_widget("Đã chọn", "selected")

        # Add to layout with equal stretch
        groups_layout.addWidget(enabled_group, 1)
        groups_layout.addWidget(disabled_group, 1)
        groups_layout.addWidget(selected_group, 1)

        scroll_layout.addLayout(groups_layout)
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)

        # Thêm stretch ở đây (giữa scroll area và buttons) để đẩy buttons xuống đáy
        main_layout.addStretch()

        # Buttons layout
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.apply_save_button = RippleButton("Áp dụng và lưu")
        self.apply_save_button.setStyleSheet("background-color: #4CAF50; color: white; padding: 8px 16px; border-radius: 4px;")
        self.apply_save_button.set_ripple_color(QColor(255, 255, 255, 120))
        self.apply_save_button.clicked.connect(self.apply_and_save_changes)

        self.reset_button = RippleButton("Reset mặc định")
        self.reset_button.setStyleSheet("background-color: #FF9800; color: white; padding: 8px 16px; border-radius: 4px;")
        self.reset_button.set_ripple_color(QColor(255, 255, 255, 120))
        self.reset_button.clicked.connect(self.reset_to_default)
        
        self.apply_shutdown_button = RippleButton("Tắt má&y")
        self.apply_shutdown_button.setStyleSheet("background-color: #e1160f; color: white; padding: 8px 16px; border-radius: 4px;")
        self.apply_shutdown_button.set_ripple_color(QColor(255, 255, 255, 120))
        self.apply_shutdown_button.clicked.connect(self.on_shutdown_button_clicked)

        # Thêm stretch để đẩy các nút sang bên phải
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.apply_save_button)
        buttons_layout.addWidget(self.reset_button)
        buttons_layout.addWidget(self.apply_shutdown_button)

        main_layout.addLayout(buttons_layout)
    def on_shutdown_button_clicked(self):
        """Xử lý sự kiện khi nhấn nút Tắt máy."""
        os.system("shutdown now")
        
    def create_color_group(self, title, state_key, layout):
        """Tạo và thêm group box vào layout (phương thức cũ để tương thích)."""
        group_box = self.create_color_group_widget(title, state_key)
        layout.addWidget(group_box)

    def create_color_group_widget(self, title, state_key):
        """Tạo QGroupBox cho một nhóm màu sắc và trả về widget."""
        group_box = QGroupBox(title)
        group_box.setStyleSheet("""
            QGroupBox {
                color: white; 
                font-weight: bold;
                background-color: rgba(50, 50, 50, 180);
                border: 2px solid rgba(100, 100, 100, 150);
                border-radius: 8px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: white;
                font-weight: bold;
                font-size: 5px;
            }
        """)
        
        # Set font size trực tiếp cho group box title
        font = group_box.font()
        font.setPointSize(15)
        font.setBold(True)
        group_box.setFont(font)
        
        group_box.setMaximumHeight(400)  # Giới hạn chiều cao tối đa
        
        # Tạo layout chính dạng dọc
        main_layout = QVBoxLayout(group_box)
        main_layout.setSpacing(0)  # Giảm spacing để đường kẻ liền kề
        main_layout.setContentsMargins(10, 10, 10, 10)

        state_config = self.config.get('ButtonColors', {}).get(state_key, {})

        # Row 1: Top color
        row1_layout = QHBoxLayout()
        row1_layout.setSpacing(20)
        
        top_label = QLabel("Màu chính")
        top_label.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
        top_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        top_label.setFixedWidth(140)  # Fixed width for consistent alignment
        
        top_container = QHBoxLayout()
        top_button = QPushButton()
        top_button.setFixedSize(60, 30)
        self._update_color_button_style(top_button, state_config.get('top_color', '#ffffff'))
        top_button.clicked.connect(lambda: self.choose_color(state_key, 'top_color', top_button))
        self.color_buttons[f"{state_key}_top"] = top_button
        
        top_code_edit = QLineEdit(state_config.get('top_color', '#ffffff'))
        top_code_edit.setStyleSheet("color: white; background-color: rgba(60, 60, 60, 150); border: 1px solid #555555; border-radius: 3px; padding: 2px; min-width: 80px; max-width: 80px;")
        top_code_edit.setAlignment(Qt.AlignCenter)
        top_code_edit.textChanged.connect(lambda text, sk=state_key, ck='top_color', edit=top_code_edit, btn=top_button: self.on_color_code_changed(text, sk, ck, edit, btn))
        self.color_buttons[f"{state_key}_top_code"] = top_code_edit
        
        top_container.addStretch()
        top_container.addWidget(top_button)
        top_container.addWidget(top_code_edit)
        top_container.addStretch()
        
        row1_layout.addWidget(top_label)
        row1_layout.addLayout(top_container)
        main_layout.addLayout(row1_layout)
        
        # Đường kẻ ngang 1 (chạy qua toàn bộ width)
        line1 = self._create_horizontal_line()
        main_layout.addWidget(line1)
        
        # Row 2: Border color
        row2_layout = QHBoxLayout()
        row2_layout.setSpacing(20)
        
        border_label = QLabel("Màu viền")
        border_label.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
        border_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        border_label.setFixedWidth(140)
        
        border_container = QHBoxLayout()
        border_button = QPushButton()
        border_button.setFixedSize(60, 30)
        self._update_color_button_style(border_button, state_config.get('border_color', '#30ffffff'))
        border_button.clicked.connect(lambda: self.choose_color(state_key, 'border_color', border_button))
        self.color_buttons[f"{state_key}_border"] = border_button
        
        border_code_edit = QLineEdit(state_config.get('border_color', '#30ffffff'))
        border_code_edit.setStyleSheet("color: white; background-color: rgba(60, 60, 60, 150); border: 1px solid #555555; border-radius: 3px; padding: 2px; min-width: 80px; max-width: 80px;")
        border_code_edit.setAlignment(Qt.AlignCenter)
        border_code_edit.textChanged.connect(lambda text, sk=state_key, ck='border_color', edit=border_code_edit, btn=border_button: self.on_color_code_changed(text, sk, ck, edit, btn))
        self.color_buttons[f"{state_key}_border_code"] = border_code_edit
        
        border_container.addStretch()
        border_container.addWidget(border_button)
        border_container.addWidget(border_code_edit)
        border_container.addStretch()
        
        row2_layout.addWidget(border_label)
        row2_layout.addLayout(border_container)
        main_layout.addLayout(row2_layout)
        
        # Đường kẻ ngang 2
        line2 = self._create_horizontal_line()
        main_layout.addWidget(line2)
        
        # Row 3: Icon color
        row3_layout = QHBoxLayout()
        row3_layout.setSpacing(20)
        
        icon_label = QLabel("Màu icon")
        icon_label.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
        icon_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        icon_label.setFixedWidth(140)
        
        icon_container = QHBoxLayout()
        icon_button = QPushButton()
        icon_button.setFixedSize(60, 30)
        self._update_color_button_style(icon_button, state_config.get('icon_color', '#ffffff'))
        icon_button.clicked.connect(lambda: self.choose_color(state_key, 'icon_color', icon_button))
        self.color_buttons[f"{state_key}_icon"] = icon_button
        
        icon_code_edit = QLineEdit(state_config.get('icon_color', '#ffffff'))
        icon_code_edit.setStyleSheet("color: white; background-color: rgba(60, 60, 60, 150); border: 1px solid #555555; border-radius: 3px; padding: 2px; min-width: 80px; max-width: 80px;")
        icon_code_edit.setAlignment(Qt.AlignCenter)
        icon_code_edit.textChanged.connect(lambda text, sk=state_key, ck='icon_color', edit=icon_code_edit, btn=icon_button: self.on_color_code_changed(text, sk, ck, edit, btn))
        self.color_buttons[f"{state_key}_icon_code"] = icon_code_edit
        
        icon_container.addStretch()
        icon_container.addWidget(icon_button)
        icon_container.addWidget(icon_code_edit)
        icon_container.addStretch()
        
        row3_layout.addWidget(icon_label)
        row3_layout.addLayout(icon_container)
        main_layout.addLayout(row3_layout)
        
        # Đường kẻ ngang 3
        line3 = self._create_horizontal_line()
        main_layout.addWidget(line3)
        
        # Row 4: Text color
        row4_layout = QHBoxLayout()
        row4_layout.setSpacing(20)
        
        text_label = QLabel("Màu text")
        text_label.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
        text_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        text_label.setFixedWidth(140)
        
        text_container = QHBoxLayout()
        text_button = QPushButton()
        text_button.setFixedSize(60, 30)
        self._update_color_button_style(text_button, state_config.get('text_color', '#ffffff'))
        text_button.clicked.connect(lambda: self.choose_color(state_key, 'text_color', text_button))
        self.color_buttons[f"{state_key}_text"] = text_button
        
        text_code_edit = QLineEdit(state_config.get('text_color', '#ffffff'))
        text_code_edit.setStyleSheet("color: white; background-color: rgba(60, 60, 60, 150); border: 1px solid #555555; border-radius: 3px; padding: 2px; min-width: 80px; max-width: 80px;")
        text_code_edit.setAlignment(Qt.AlignCenter)
        text_code_edit.textChanged.connect(lambda text, sk=state_key, ck='text_color', edit=text_code_edit, btn=text_button: self.on_color_code_changed(text, sk, ck, edit, btn))
        self.color_buttons[f"{state_key}_text_code"] = text_code_edit
        
        text_container.addStretch()
        text_container.addWidget(text_button)
        text_container.addWidget(text_code_edit)
        text_container.addStretch()
        
        row4_layout.addWidget(text_label)
        row4_layout.addLayout(text_container)
        main_layout.addLayout(row4_layout)
        
        # Đường kẻ ngang 4
        line4 = self._create_horizontal_line()
        main_layout.addWidget(line4)
        
        # Row 5: Icon alpha
        row5_layout = QHBoxLayout()
        row5_layout.setSpacing(20)
        
        alpha_label = QLabel("Độ trong suốt icon")
        alpha_label.setStyleSheet("color: white; font-weight: bold; padding: 5px;")
        alpha_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        alpha_label.setFixedWidth(140)
        
        alpha_container = QHBoxLayout()
        alpha_spin = QSpinBox()
        alpha_spin.setRange(0, 255)
        alpha_spin.setValue(state_config.get('icon_alpha', 48))
        alpha_spin.setStyleSheet("""
            QSpinBox {
                color: white; 
                background-color: #333333; 
                border: 1px solid #555555;
                border-radius: 3px;
                padding: 2px;
                min-width: 60px;
                max-width: 60px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                background-color: #555555;
                border: none;
                width: 15px;
            }
            QSpinBox::up-button:hover, QSpinBox::down-button:hover {
                background-color: #777777;
            }
        """)
        alpha_spin.valueChanged.connect(lambda value, sk=state_key: self.update_alpha(sk, 'icon_alpha', value))
        self.alpha_spins[state_key] = alpha_spin
        alpha_container.addStretch()
        alpha_container.addWidget(alpha_spin)
        alpha_container.addStretch()
        
        row5_layout.addWidget(alpha_label)
        row5_layout.addLayout(alpha_container)
        main_layout.addLayout(row5_layout)

        return group_box

    def _create_horizontal_line(self):
        """Tạo đường kẻ ngang để phân tách các hàng."""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setStyleSheet("""
            QFrame {
                color: rgba(150, 150, 150, 100);
                background-color: rgba(150, 150, 150, 100);
                max-height: 1px;
                margin: 2px 0px;
            }
        """)
        return line

    def choose_color(self, state_key, color_key, button):
        current_color = self.config.get('ButtonColors', {}).get(state_key, {}).get(color_key, '#ffffff')
        if current_color.startswith('#'):
            color = QColor(current_color)
        else:
            color = QColor()
            color.setNamedColor(current_color)
        
        color = QColorDialog.getColor(color, self, f"Chọn màu cho {color_key}")
        if color.isValid():
            color_hex = color.name()
            self.config['ButtonColors'][state_key][color_key] = color_hex
            
            # Cập nhật hiển thị màu với style luôn đảm bảo button có thể bấm được
            self._update_color_button_style(button, color_hex)
            button.repaint()  # Force immediate repaint
            
            # Cập nhật color code edit - sửa lại key mapping
            # Từ 'top_color' -> 'top', 'border_color' -> 'border', etc.
            color_type = color_key.replace('_color', '')  # top_color -> top
            code_edit_key = f"{state_key}_{color_type}_code"
            if code_edit_key in self.color_buttons:
                # Temporarily disconnect signal to avoid triggering textChanged
                code_edit = self.color_buttons[code_edit_key]
                code_edit.blockSignals(True)
                code_edit.setText(color_hex)
                code_edit.blockSignals(False)

    def on_color_code_changed(self, text, state_key, color_key, code_edit, color_button):
        """Xử lý khi mã màu được thay đổi trực tiếp."""
        if self._is_valid_hex_color(text):
            # Cập nhật config
            self.config['ButtonColors'][state_key][color_key] = text
            
            # Cập nhật color button style
            self._update_color_button_style(color_button, text)
            color_button.repaint()
            
            # Đặt màu nền của QLineEdit thành bình thường khi hợp lệ
            code_edit.setStyleSheet("color: white; background-color: rgba(60, 60, 60, 150); border: 1px solid #555555; border-radius: 3px; padding: 2px; min-width: 80px; max-width: 80px;")
        else:
            # Đặt màu nền đỏ khi không hợp lệ
            code_edit.setStyleSheet("color: white; background-color: rgba(150, 60, 60, 150); border: 1px solid #ff5555; border-radius: 3px; padding: 2px; min-width: 80px; max-width: 80px;")

    def _is_valid_hex_color(self, color_code):
        """Kiểm tra xem mã màu hex có hợp lệ không."""
        import re
        # Regex cho hex color: #RGB, #RRGGBB, #RRGGBBAA
        hex_pattern = r'^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6}|[A-Fa-f0-9]{8})$'
        return re.match(hex_pattern, color_code) is not None

    def update_alpha(self, state_key, alpha_key, value):
        """Cập nhật giá trị alpha."""
        if 'ButtonColors' not in self.config:
            self.config['ButtonColors'] = {}
        if state_key not in self.config['ButtonColors']:
            self.config['ButtonColors'][state_key] = {}
        self.config['ButtonColors'][state_key][alpha_key] = value

    def _update_color_button_style(self, button, color_hex):
        """Cập nhật style cho color button để luôn có thể bấm được."""
        # Tạo style với viền đen và background là màu được chọn
        # Thêm hiệu ứng hover để rõ ràng hơn
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {color_hex};
                border: 2px solid #000000;
                border-radius: 3px;
            }}
            QPushButton:hover {{
                border: 2px solid #ffffff;
                background-color: {color_hex};
            }}
            QPushButton:pressed {{
                border: 2px solid #cccccc;
                background-color: {color_hex};
            }}
        """)

    def apply_and_save_changes(self):
        """Áp dụng và lưu thay đổi cùng lúc."""
        # Disable nút trong thời gian xử lý
        self.apply_save_button.setEnabled(False)
        
        # Sử dụng QTimer để tạo delay
        QTimer.singleShot(100, lambda: self._perform_apply_and_save_changes())

    def _perform_apply_and_save_changes(self):
        """Thực hiện áp dụng và lưu thay đổi sau hiệu ứng."""
        try:
            # Đầu tiên lưu config vào file
            config_path = resource_path('config.yaml')
            with open(config_path, 'w', encoding='utf-8') as file:
                yaml.safe_dump(self.config, file, default_flow_style=False, allow_unicode=True)
            
            # Sau đó áp dụng thay đổi vào main tab
            if self.main_tab:
                # Reload button colors in bullet widget
                if hasattr(self.main_tab.bullet_widget, 'update_button_colors'):
                    self.main_tab.bullet_widget.update_button_colors()
                
                # Update main_tab's config
                self.main_tab.config['ButtonColors'] = self.config['ButtonColors']
                # Trigger update of button states
                self.main_tab._update_action_buttons_state()
                # Force repaint all buttons to ensure changes are visible immediately
                self.main_tab.ok_button.repaint()
                self.main_tab.cancel_button.repaint()
                self.main_tab.launch_all_button.repaint()
                self.main_tab.calculator_button.repaint()
                
                # Force repaint main window and all its children
                self.main_tab.repaint()
                self.main_tab.update()
                
                # Force repaint the entire application window
                if hasattr(self.main_tab, 'parent') and self.main_tab.parent():
                    self.main_tab.parent().repaint()
                    self.main_tab.parent().update()
            
            # Khôi phục trạng thái nút sau khi hoàn thành
            QTimer.singleShot(500, lambda: self._restore_apply_save_button())
            
        except Exception as e:
            # Khôi phục nút và log lỗi
            self._restore_apply_save_button()
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(f"Không thể áp dụng và lưu config: {str(e)}", "ERROR")
            # Bỏ popup, chỉ log

    def _restore_apply_save_button(self):
        """Khôi phục trạng thái ban đầu của nút áp dụng và lưu."""
        self.apply_save_button.setEnabled(True)

    def reset_to_default(self):
        """Reset về cài đặt mặc định từ default.yaml."""
        # Disable nút trong thời gian xử lý
        self.reset_button.setEnabled(False)
        
        # Sử dụng QTimer để tạo delay
        QTimer.singleShot(100, lambda: self._perform_reset_to_default())

    def _perform_reset_to_default(self):
        """Thực hiện reset về mặc định sau hiệu ứng."""
        try:
            default_path = resource_path('default.yaml')
            with open(default_path, 'r', encoding='utf-8') as file:
                default_config = yaml.safe_load(file)
            
            # Update current config with default ButtonColors
            self.config['ButtonColors'] = default_config.get('ButtonColors', {})
            
            # Update UI buttons
            self.update_ui_from_config()
            
            # Reload button colors in bullet widget after reset
            if self.main_tab and hasattr(self.main_tab.bullet_widget, 'update_button_colors'):
                self.main_tab.bullet_widget.update_button_colors()
            
            # Update main_tab's config and trigger updates
            if self.main_tab:
                self.main_tab.config['ButtonColors'] = self.config['ButtonColors']
                self.main_tab._update_action_buttons_state()
                
                # Force repaint all buttons
                self.main_tab.ok_button.repaint()
                self.main_tab.cancel_button.repaint()
                self.main_tab.launch_all_button.repaint()
                self.main_tab.calculator_button.repaint()
                self.main_tab.repaint()
                self.main_tab.update()
                
                # Force repaint the entire application window
                if hasattr(self.main_tab, 'parent') and self.main_tab.parent():
                    self.main_tab.parent().repaint()
                    self.main_tab.parent().update()
            
            # Khôi phục trạng thái nút sau khi hoàn thành
            QTimer.singleShot(500, lambda: self._restore_reset_button())
            
        except Exception as e:
            # Khôi phục nút và log lỗi
            self._restore_reset_button()
            from ui.tabs.event_log_tab import LogTab
            LogTab.log(f"Không thể load default config: {str(e)}", "ERROR")
            # Bỏ popup, chỉ log

    def _restore_reset_button(self):
        """Khôi phục trạng thái ban đầu của nút reset."""
        self.reset_button.setEnabled(True)

    def update_ui_from_config(self):
        """Cập nhật UI từ config hiện tại."""
        for state_key in ['enabled', 'disabled', 'selected']:
            state_config = self.config.get('ButtonColors', {}).get(state_key, {})
            
            # Update top color button
            top_color = state_config.get('top_color', '#ffffff')
            if f"{state_key}_top" in self.color_buttons:
                self._update_color_button_style(self.color_buttons[f"{state_key}_top"], top_color)
            if f"{state_key}_top_code" in self.color_buttons:
                self.color_buttons[f"{state_key}_top_code"].setText(top_color)
            
            # Update border color button
            border_color = state_config.get('border_color', '#30ffffff')
            if f"{state_key}_border" in self.color_buttons:
                self._update_color_button_style(self.color_buttons[f"{state_key}_border"], border_color)
            if f"{state_key}_border_code" in self.color_buttons:
                self.color_buttons[f"{state_key}_border_code"].setText(border_color)
            
            # Update icon color button
            icon_color = state_config.get('icon_color', '#ffffff')
            if f"{state_key}_icon" in self.color_buttons:
                self._update_color_button_style(self.color_buttons[f"{state_key}_icon"], icon_color)
            if f"{state_key}_icon_code" in self.color_buttons:
                self.color_buttons[f"{state_key}_icon_code"].setText(icon_color)
            
            # Update text color button
            text_color = state_config.get('text_color', '#ffffff')
            if f"{state_key}_text" in self.color_buttons:
                self._update_color_button_style(self.color_buttons[f"{state_key}_text"], text_color)
            if f"{state_key}_text_code" in self.color_buttons:
                self.color_buttons[f"{state_key}_text_code"].setText(text_color)
            
            # Update alpha spin box
            if state_key in self.alpha_spins:
                alpha = state_config.get('icon_alpha', 48)
                self.alpha_spins[state_key].setValue(alpha)
