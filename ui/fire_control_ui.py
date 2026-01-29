#-*- coding: utf-8 -*-



import yaml
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor, QBrush, QLinearGradient
from PyQt5.QtCore import Qt, QRectF

# Updated imports for new file structure
from ui.widgets.features.compass_widget import AngleCompass, resource_path
from ui.widgets.features.half_compass_widget import HalfCircleWidget
from ui.widgets.features.ammunition_widget import BulletWidget
from ui.widgets.features.numeric_display_widget import NumericDataWidget
from ui.widgets.components.custom_message_box_widget import CustomMessageBox
from ui.widgets.components.buttons.isometric import SVGColorChanger, ColoredSVGButton
import ui.ui_config as config
from communication.data_sender import sender_ammo_status, sender_angle_direction
from ui.views.main_control_tab import MainTab, GridBackgroundWidget
from ui.views.system_info_tab import InfoTab
from ui.views.event_log_tab import LogTab
from ui.views.settings_tab import SettingTab

class FireControl(QtCore.QObject):
    def __init__(self):
        # Đọc file config
        super().__init__()
        with open(resource_path(r'config.yaml'), 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)

        # Load unified configuration system
        try:
            from data_management.unified_threshold_manager import unified_threshold_manager
            unified_threshold_manager.load_config()
        except ImportError:
            print("Không thể tải unified threshold manager")

    def setupUi(self, MainWindow):
        # Đảm bảo mw_width và total_h luôn có giá trị trước khi dùng ở bất kỳ đâu
        try:
            mw_width = self.config['MainWindow']['width']
        except Exception:
            try:
                mw_width = MainWindow.width()
                if mw_width <= 0:
                    mw_width = 1280
            except Exception:
                mw_width = 1280
        try:
            total_h = self.config['MainWindow']['height']
        except Exception:
            try:
                total_h = MainWindow.height()
                if total_h <= 0:
                    total_h = 800
            except Exception:
                total_h = 800
        # Cấu hình MainWindow từ config
        MainWindow.setObjectName("FireControl")
        # # Vô hiệu hóa nút thoát và thu nhỏ
        # MainWindow.setWindowFlags(
        #     QtCore.Qt.Window |
        #     QtCore.Qt.CustomizeWindowHint |
        #     QtCore.Qt.WindowTitleHint
        # )
        
        if self.config['MainWindow']['fixed']:
            MainWindow.setFixedSize(self.config['MainWindow']['width'],
                self.config['MainWindow']['height']
            )
        else:
            MainWindow.resize(self.config['MainWindow']['width'], 
                self.config['MainWindow']['height']
            )
        # --- SettingPage: dùng nút setting (icon ⚙) để mở giao diện chỉnh màu ---
    # ...existing code...
        
        
        # Thay đổi màu nền background thành #121212
        style = self.config['MainWindow']['style']
        # Nếu style đã có background, thay thế, nếu chưa thì thêm vào
        import re
        if 'background' in style:
            style = re.sub(r'background[^;]*;', 'background: #121212;', style)
        else:
            style += ' background: #121212;'
        MainWindow.setStyleSheet(style)
        # Đặt icon cửa sổ là cờ Việt Nam, kiểm tra file icon
        from PyQt5.QtGui import QIcon, QPixmap
        icon_path = resource_path('assets/Icons/Vietnam.png')
        pixmap = QPixmap(icon_path)
        if pixmap.isNull():
            print(f"[LỖI] Không load được icon: {icon_path}. Hãy kiểm tra file PNG, kích thước và đường dẫn.")
        else:
            MainWindow.setWindowIcon(QIcon(pixmap))
        
        # Đọc cấu hình background animation từ config
        background_animation_enabled = self.config['MainWindow'].get('background_animation', True)
        
        tab_height = 34
        
        self.main_tab = MainTab(self.config, MainWindow)
        self.main_tab.setGeometry(0, tab_height, mw_width, total_h - tab_height)
        self.centralwidget = self.main_tab

        # --- Chrome-like top tab bar (full-width) ---
        # Create a lightweight tab bar overlay at the top of the central widget.
        # Đảm bảo mw_width luôn có giá trị
        try:
            mw_width = self.config['MainWindow']['width']
        except Exception:
            try:
                mw_width = MainWindow.width()
                if mw_width <= 0:
                    mw_width = 1280
            except Exception:
                mw_width = 1280

        # Parent the tab bar to the MainWindow so it stays above central widget content
        self.tab_bar = QtWidgets.QWidget(MainWindow)
        self.tab_bar.setObjectName("tab_bar")
        self.tab_bar.setGeometry(0, 0, mw_width, tab_height)
        self.tab_bar.setStyleSheet("background: #1e5c6b; border-bottom: none;")

        # --- Line trắng dưới tab bar, tạo border liền mạch ---
        self.left_line = QtWidgets.QWidget(MainWindow)
        self.left_line.setStyleSheet("background: #fff;")
        self.right_line = QtWidgets.QWidget(MainWindow)
        self.right_line.setStyleSheet("background: #fff;")
        self.left_line.setFixedHeight(1)
        self.right_line.setFixedHeight(1)
        # Đặt vị trí line theo tab Main (tab_active) khi khởi tạo
        self.left_line.show()
        self.right_line.show()
        # Đảm bảo cập nhật vị trí line khi khởi tạo
        QtCore.QTimer.singleShot(0, self._update_tab_lines)

        self.tab_activating = QtWidgets.QPushButton("Điều khiển", self.tab_bar)
        self.tab_activating.setCursor(Qt.PointingHandCursor)
        tab_width = 220
        self.tab_activating.setGeometry(8, 6, tab_width, 28)
        # Initial selected style for Main tab: dark background with white top/side borders but NO bottom border
        # The content area below will provide the continuous white top border across the full width.
        self.tab_activating.setStyleSheet(
            "QPushButton{ background: #121212; color: #E6EEF3; border-left: 1px solid #FFFFFF; border-right: 1px solid #FFFFFF; border-top: 1px solid #FFFFFF; border-bottom: none; "
            "border-top-left-radius:8px; border-top-right-radius:8px; padding-left:12px; }"
        )

        # Right tab: 'Thông tin' (empty page)
        self.tab_other = QtWidgets.QPushButton("Thông tin", self.tab_bar)
        self.tab_other.setCursor(Qt.PointingHandCursor)
        # place it directly to the right of the active tab (adjacent)
        gap = 8
        active_geo = self.tab_activating.geometry()
        other_x = active_geo.x() + self.tab_activating.width() + gap
        self.tab_other.setGeometry(other_x, 6, tab_width, 28)
        # Inactive tab should visually match the page background (slightly black) so it blends
        # with the app body as requested.
        # Initial inactive style for Thông tin tab
        self.tab_other.setStyleSheet(
            "QPushButton{ background: transparent; color: rgba(230,238,243,0.7); border: none; padding-left:12px; border-top-left-radius:8px; border-top-right-radius:8px; }"
            "QPushButton:hover{ color: #E6EEF3; }"
        )

        self.tab_log = QtWidgets.QPushButton("Lịch sử", self.tab_bar)
        self.tab_log.setCursor(Qt.PointingHandCursor)
        # Place it directly to the right of the 'Thông tin' tab
        log_x = other_x + self.tab_other.width() + gap
        self.tab_log.setGeometry(log_x, 6, tab_width, 28)  # Set vertical position to 6
        # Initial inactive style for Log tab
        self.tab_log.setStyleSheet(
            "QPushButton{ background: #121212; color: #E6EEF3; border: none; padding-left:12px; border-top-left-radius:8px; border-top-right-radius:8px; font-weight:600; }"
            "QPushButton:hover{ color: #E6EEF3; }"
        )
        
        # Thêm chấm đỏ báo lỗi cho tab lịch sử (ban đầu ẩn)
        self.error_indicator = QtWidgets.QLabel(self.tab_log)
        self.error_indicator.setFixedSize(10, 10)
        self.error_indicator.setStyleSheet(
            "background-color: #EF4444; border-radius: 5px;"
        )
        # Đặt vị trí chấm đỏ ở cuối tab (đuôi tab), cách lề phải 12px, căn giữa theo chiều cao
        # tab_width = 220, cách lề phải 12px, chấm đỏ 10px => 220 - 12 - 10 = 198
        self.error_indicator.move(198, 9)  # y=9 để căn giữa theo chiều cao (28px tab height)
        self.error_indicator.hide()  # Ẩn ban đầu

        self.tab_settings = QtWidgets.QPushButton("Cài đặt", self.tab_bar)
        self.tab_settings.setCursor(Qt.PointingHandCursor)
        settings_x = self.tab_log.geometry().x() + self.tab_log.width() + gap
        self.tab_settings.setGeometry(settings_x, 6, tab_width, 28)
        self.tab_settings.setStyleSheet(
            "QPushButton{ background: #121212; color: #E6EEF3; border: none; padding-left:12px; border-top-left-radius:8px; border-top-right-radius:8px; font-weight:600; }"
            "QPushButton:hover{ color: #E6EEF3; }"
        )

        # Create an empty info page below the tab bar. Initially hidden.
        # Đảm bảo total_h luôn có giá trị
        try:
            total_h = self.config['MainWindow']['height']
        except Exception:
            try:
                total_h = MainWindow.height()
                if total_h <= 0:
                    total_h = 800
            except Exception:
                total_h = 800
        self.info_page = InfoTab(self.config, MainWindow)
        self.info_page.setObjectName('info_page')
        self.info_page.setGeometry(0, tab_height, mw_width, total_h - tab_height)
        self.info_page.setStyleSheet('border-top: none;')  # Removed background to allow grid to show
        self.info_page.hide()

        # Create an empty log page below the tab bar. Initially hidden.
        self.log_page = LogTab(self.config, MainWindow)
        self.log_page.setObjectName('log_page')
        self.log_page.setGeometry(0, tab_height, mw_width, total_h - tab_height)
        self.log_page.setStyleSheet('background: #121212; border-top: none;')
        self.log_page.hide()
        
        # Lưu reference đến FireControl trong LogTab để có thể hiển thị error indicator
        LogTab.set_fire_control_instance(self)

        # Create an empty settings page below the tab bar. Initially hidden.
        self.settings_page = SettingTab(self.config, MainWindow)
        self.settings_page.setObjectName('settings_page')
        self.settings_page.setGeometry(0, tab_height, mw_width, total_h - tab_height)
        self.settings_page.setStyleSheet('background: #121212; border-top: none;')
        self.settings_page.hide()
        
        # Set reference to main_tab for settings page
        self.settings_page.main_tab = self.main_tab



        # Wire tab clicks to swap pages
        self.tab_activating.clicked.connect(lambda: self._show_main_tab())
        self.tab_other.clicked.connect(lambda: self._show_info_tab())
        self.tab_log.clicked.connect(lambda: self._show_log_tab())
        self.tab_settings.clicked.connect(lambda: self._show_settings_tab())

        # Ensure the tab bar stays above other children
        self.tab_bar.raise_()

        MainWindow.setCentralWidget(self.centralwidget)

        self.tab_bar.installEventFilter(self)
        self.tab_activating.installEventFilter(self)
        self.tab_other.installEventFilter(self)

        # Show the main tab initially
        self._show_main_tab()


    def _update_tab_styles(self, active_tab):
        """Cập nhật style cho các tab dựa trên tab đang active."""
        tabs = [self.tab_activating, self.tab_other, self.tab_log, self.tab_settings]
        for tab in tabs:
            if tab == active_tab:
                tab.setStyleSheet(
                    "QPushButton{ background: #121212; color: #E6EEF3; border: 1px solid #FFFFFF; border-bottom: none; "
                    "border-top-left-radius:8px; border-top-right-radius:8px; padding-left:12px; font-weight:600; }"
                )
            else:
                tab.setStyleSheet(
                    "QPushButton{ background: #121212; color: #E6EEF3; border: none; padding-left:12px; border-top-left-radius:8px; border-top-right-radius:8px; font-weight:600; }"
                    "QPushButton:hover{ color: #E6EEF3; }"
                )

    def _show_main_tab(self):
        """Hiển thị tab chính và cập nhật style."""
        try:
            self.main_tab.show()
            self.info_page.hide()
            self.log_page.hide()
            self.settings_page.hide()
        except Exception:
            pass
        self._update_tab_styles(self.tab_activating)
        QtCore.QTimer.singleShot(0, self._update_tab_lines)

    def _show_info_tab(self):
        """Hiển thị tab thông tin và cập nhật style."""
        try:
            self.main_tab.hide()
            self.info_page.show()
            self.info_page.raise_()
            self.log_page.hide()
            self.settings_page.hide()
        except Exception:
            pass
        self._update_tab_styles(self.tab_other)
        QtCore.QTimer.singleShot(0, self._update_tab_lines)

    def _show_log_tab(self):
        """Hiển thị tab log và cập nhật style."""
        try:
            self.main_tab.hide()
            self.info_page.hide()
            self.log_page.show()
            self.log_page.raise_()
            self.settings_page.hide()
            # Ẩn chấm đỏ khi người dùng vào tab lịch sử
            self.error_indicator.hide()
        except Exception:
            pass
        self._update_tab_styles(self.tab_log)
        QtCore.QTimer.singleShot(0, self._update_tab_lines)

    def _show_settings_tab(self):
        """Hiển thị tab cài đặt và cập nhật style."""
        try:
            self.main_tab.hide()
            self.info_page.hide()
            self.log_page.hide()
            self.settings_page.show()
            self.settings_page.raise_()
        except Exception:
            pass
        self._update_tab_styles(self.tab_settings)
        QtCore.QTimer.singleShot(0, self._update_tab_lines)

    def show_error_indicator(self):
        """Hiển thị chấm đỏ báo lỗi trên tab lịch sử."""
        try:
            self.error_indicator.show()
            self.error_indicator.raise_()  # Đảm bảo chấm đỏ hiển thị trên cùng
        except Exception as e:
            print(f"Không thể hiển thị error indicator: {e}")



    def toggle_background_animation(self):
        """Bật/tắt hiệu ứng background animation."""
        current_state = self.main_tab.enable_animation
        self.main_tab.set_animation_enabled(not current_state)
        return not current_state

    def set_background_animation(self, enabled):
        """Thiết lập trạng thái hiệu ứng background animation."""
        self.main_tab.set_animation_enabled(enabled)

    def eventFilter(self, obj, event):
        if obj in (self.tab_bar, self.tab_activating, self.tab_other, self.tab_log) and event.type() in (QtCore.QEvent.Move, QtCore.QEvent.Resize, QtCore.QEvent.Show):
            self._update_tab_lines()
        return super().eventFilter(obj, event)



    def _update_tab_lines(self):
        """Cập nhật vị trí và kích thước của 2 line trắng dưới tab bar, chạy theo tab đang active."""
        # Xác định tab nào đang active dựa vào style (có border trắng là active)
        if 'border: 1px solid #FFFFFF' in self.tab_activating.styleSheet():
            tab_geo = self.tab_activating.geometry()
        elif 'border: 1px solid #FFFFFF' in self.tab_log.styleSheet():
            tab_geo = self.tab_log.geometry()
        elif 'border: 1px solid #FFFFFF' in self.tab_settings.styleSheet():
            tab_geo = self.tab_settings.geometry()
        else:
            tab_geo = self.tab_other.geometry()
        bar_geo = self.tab_bar.geometry()
        y = bar_geo.y() + bar_geo.height() - 1  # ngay dưới tab bar
        h = 2  # độ dày line
        # Line trái: từ mép trái tab bar đến mép trái tab đang active
        self.left_line.setGeometry(bar_geo.x(), y, tab_geo.x() - bar_geo.x(), h)
        # Line phải: từ mép phải tab active đến hết tab bar
        right_x = tab_geo.x() + tab_geo.width()
        self.right_line.setGeometry(right_x, y, bar_geo.width() - (right_x - bar_geo.x()), h)
        self.left_line.raise_()
        self.right_line.raise_()
