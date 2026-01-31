from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QPushButton, QLabel
from PyQt5.QtCore import Qt, QRectF
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient
from ..widgets.features.compass_widget import AngleCompass
from ..widgets.features.vertical_compass_widget import VerticalCompassWidget
from ..widgets.features.numeric_display_widget import NumericDataWidget
from ..widgets.features.bullet_widget import BulletWidget
from ..widgets.components.custom_message_box_widget import CustomMessageBox, ConfirmationWidget
from .ballistic_calculator_dialog import BallisticCalculatorWidget
from .angle_input_dialog import AngleInputDialog
from ..widgets.components.buttons.isometric import ColoredSVGButton
import ui.ui_config as config
from communication.data_sender import sender_angle_direction, sender_ammo_status
from communication.can_config import CAN_ID_ANGLE_LEFT, CAN_ID_ANGLE_RIGHT
import communication.can_config as CONFIG
import yaml
import random
import math
from common.utils import resource_path, get_firing_table_interpolator, load_firing_table


class MainTab(GridBackgroundWidget):
    def __init__(self, config_data, parent=None):
        super().__init__(parent, enable_animation=config_data['MainWindow'].get('background_animation', True))
        self.config = config_data
        self._data_timer = None  # Thêm biến timer
        self._buttons_active_state = False  # Theo dõi trạng thái hiện tại của OK/Cancel button
        self._launch_all_active_state = False  # Theo dõi trạng thái hiện tại của Launch All button
        
        # Lưu lượng sửa từ ballistic calculator
        self.elevation_correction_left = 0
        self.elevation_correction_right = 0
        self.direction_correction_left = 0
        self.direction_correction_right = 0
        
        self.setupUi()

    def setupUi(self):
        # Tạo các compass từ config
        compass_left_config = self.config['Widgets']['CompassLeft']
        # redlines sử dụng góc compass (0° = Bắc/trên, tăng theo chiều kim đồng hồ)
        self.compass_left = AngleCompass(35, 35, compass_left_config.get('redlines', [210, 360]), 0, self)
        
        self.compass_left.setGeometry(QtCore.QRect(
            compass_left_config['x'], compass_left_config['y'] + 34,
            compass_left_config['width'], compass_left_config['height'])
        )
        
        self.compass_left.setStyleSheet(compass_left_config['style'])

        half_left_config = self.config['Widgets']['HalfCompassLeft']
        # Tính toán redline limits từ CompassLeft redlines
        # redlines sử dụng góc compass (0° = Bắc/trên, tăng theo chiều kim đồng hồ)
        # Công thức: redline[0] - 90 = min_limit, 450 - redline[1] = max_limit
        compass_left_redlines = compass_left_config.get('redlines', [])
        left_min_limit = -compass_left_redlines[0] # 150 - 90 = 60, nên -60
        left_max_limit = compass_left_redlines[1]     # 450 - 385 = 65
        left_redline_limits = [left_min_limit, left_max_limit]
        
        # Giới hạn cho góc tầm: làm xám các vạch ngoài khoảng [10, 60]

        elevation_limits = self.config['Widgets']['LimitAngles'].get('Elevation', [])
        self.half_compass_left = VerticalCompassWidget(15, 20, self, 
                                                   redline_limits=left_redline_limits,
                                                   elevation_limits=elevation_limits)
        
        # Điều chỉnh vị trí để căn chỉnh chính xác với compass và cùng y với HalfCompassLeft
        self.half_compass_left.setGeometry(QtCore.QRect(
            half_left_config['x'],  # Sử dụng x từ config
            half_left_config['y'] + 30,  # Cùng offset với các widget khác
            half_left_config['width'], half_left_config['height'])
        )
        
        self.half_compass_left.setStyleSheet(half_left_config['style'])

        # Thêm nút nhập khoảng cách cho half compass trái
        # Tính toán chiều rộng nút bằng với tổng chiều rộng của 2 wheel + spacing
        # wheel_width = total_width * 0.25, có 2 wheel, spacing = 20
        # total_wheel_width = 2 * wheel_width + spacing = total_width * 0.5 + 20
        button_width_left = half_left_config['width'] * 0.5 + 20
        button_x_left = half_left_config['x'] + (half_left_config['width'] - button_width_left) / 2
        
        # Khoảng cách từ wheel đến khung số là 5px
        # Khung số có chiều cao 20px, cách wheel 5px từ đáy wheel
        # Nút nằm dưới khung số với khoảng cách 2px
        button_y_offset_left = -5  # 5px (wheel->khung) + 20px (chiều cao khung) + 2px (khung->nút)
        
        self.angle_input_button_left = QPushButton("Nhập Cự ly - Góc", self)
        self.angle_input_button_left.setGeometry(QtCore.QRect(
            int(button_x_left),
            half_left_config['y'] + 30 + half_left_config['height'] + button_y_offset_left,
            int(button_width_left),
            25  # Chiều cao 25px
        ))
        self.angle_input_button_left.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.angle_input_button_left.clicked.connect(lambda: self.on_angle_input_clicked('left'))

        compass_right_config = self.config['Widgets']['CompassRight']
        # redlines sử dụng góc compass (0° = Bắc/trên, tăng theo chiều kim đồng hồ)
        self.compass_right = AngleCompass(45, 40, compass_right_config.get('redlines', [180, 330]), 0, self)
        
        self.compass_right.setGeometry(QtCore.QRect(
            compass_right_config['x'], compass_right_config['y'] + 34,
            compass_right_config['width'], compass_right_config['height'])
        )
        
        self.compass_right.setStyleSheet(compass_right_config['style'])

        half_right_config = self.config['Widgets']['HalfCompassRight']
        # Tính toán redline limits từ CompassRight redlines
        # redlines sử dụng góc compass (0° = Bắc/trên, tăng theo chiều kim đồng hồ)
        # Công thức: redline[0] - 90 = min_limit, 450 - redline[1] = max_limit
        compass_right_redlines = compass_right_config.get('redlines', [155, 390])
        right_min_limit = -compass_right_redlines[0]  # 155 - 90 = 65, nên -65
        right_max_limit = compass_right_redlines[1]    # 450 - 390 = 60
        right_redline_limits = [right_min_limit, right_max_limit]
        
        # Giới hạn cho góc tầm: làm xám các vạch ngoài khoảng [10, 60]
        elevation_limits = self.config['Widgets']['LimitAngles'].get('Elevation', [])
        
        self.half_compass_right = VerticalCompassWidget(30, 25, self, 
                                                    redline_limits=right_redline_limits,
                                                    elevation_limits=elevation_limits)
        
        # Điều chỉnh vị trí để có cùng y với HalfCompassLeft, dịch lên trên 10px
        self.half_compass_right.setGeometry(QtCore.QRect(
            half_right_config['x'],  # Sử dụng x từ config
            half_left_config['y'] + 30,  # Dịch lên trên 10px so với HalfCompassLeft
            half_right_config['width'], half_right_config['height'])
        )
        
        self.half_compass_right.setStyleSheet(half_right_config['style'])

        # Thêm nút nhập khoảng cách cho half compass phải
        # Tính toán chiều rộng nút bằng với tổng chiều rộng của 2 wheel + spacing
        button_width_right = half_right_config['width'] * 0.5 + 20
        button_x_right = half_right_config['x'] + (half_right_config['width'] - button_width_right) / 2
        
        # Khoảng cách từ khung số đến nút là 2px
        button_y_offset_right = -5  # 5px (wheel->khung) + 20px (chiều cao khung) + 2px (khung->nút)
        
        self.angle_input_button_right = QPushButton("Nhập Cự ly - Góc", self)
        self.angle_input_button_right.setGeometry(QtCore.QRect(
            int(button_x_right),
            half_left_config['y'] + 30 + half_right_config['height'] + button_y_offset_right,
            int(button_width_right),
            25  # Chiều cao 25px
        ))
        self.angle_input_button_right.setStyleSheet("""
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
        """)
        self.angle_input_button_right.clicked.connect(lambda: self.on_angle_input_clicked('right'))

        # Thêm NumericDataWidget từ config
        numeric_config = self.config['Widgets']['NumericDataWidget']
        self.numeric_data_widget = NumericDataWidget()
        self.numeric_data_widget.setParent(self)
        
        self.numeric_data_widget.setGeometry(QtCore.QRect(
            numeric_config['x'], numeric_config['y'] + 34,
            numeric_config['width'], numeric_config['height'])
        )

        # Thêm các nút từ config
        # OK Button (Xác nhận) với SVG icon màu trắng và hiệu ứng isometric
        ok_config = self.config['Widgets']['Buttons']['OK']
        self.ok_button = ColoredSVGButton.create_isometric_button(self)
        
        self.ok_button.setGeometry(QtCore.QRect(
            ok_config['x'], ok_config['y'] + 34,
            ok_config['width'], ok_config['height'])
        )
        
        # Sử dụng SVGColorChanger để tạo icon màu trắng với hiệu ứng isometric
        btn_colors = self.config.get('ButtonColors', {})
        enabled = btn_colors.get('enabled', {})
        ColoredSVGButton.setup_button(
            self.ok_button, 
            "assets/Icons/launch.svg",
            icon_color=enabled.get("icon_color", "#ffffff"),
            icon_alpha=enabled.get("icon_alpha", 48),
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#121212"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )

        # Cancel Button với SVG icon màu trắng và hiệu ứng isometric
        cancel_config = self.config['Widgets']['Buttons']['Cancel']
        self.cancel_button = ColoredSVGButton.create_isometric_button(self)
        
        self.cancel_button.setGeometry(QtCore.QRect(
            cancel_config['x'], cancel_config['y'] + 34,
            cancel_config['width'], cancel_config['height'])
        )
        
        # Sử dụng SVGColorChanger để tạo icon màu trắng với hiệu ứng isometric
        ColoredSVGButton.setup_button(
            self.cancel_button, 
            "assets/Icons/cancel.svg",
            icon_color=enabled.get("icon_color", "#ffffff"),
            icon_alpha=enabled.get("icon_alpha", 48),
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#121212"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )

        # Launch All Button với SVG icon màu trắng và hiệu ứng isometric
        launch_config = self.config['Widgets']['Buttons']['LaunchAll']
        self.launch_all_button = ColoredSVGButton.create_isometric_button(self)
        
        self.launch_all_button.setGeometry(QtCore.QRect(
            launch_config['x'], launch_config['y'] + 34,
            launch_config['width'], launch_config['height'])
        )
        
        # Sử dụng SVGColorChanger để tạo icon màu trắng với hiệu ứng isometric
        ColoredSVGButton.setup_button(
            self.launch_all_button, 
            "assets/Icons/launch_all.svg",
            icon_color=enabled.get("icon_color", "#ffffff"),
            icon_alpha=enabled.get("icon_alpha", 48),
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#121212"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )

        # Calculator Button với SVG icon màu trắng và hiệu ứng isometric
        calc_config = self.config['Widgets']['Buttons']['Calculator']
        self.calculator_button = ColoredSVGButton.create_isometric_button(self)
        
        self.calculator_button.setGeometry(QtCore.QRect(
            calc_config['x'], calc_config['y'] + 34,
            calc_config['width'], calc_config['height'])
        )
        
        # Sử dụng SVGColorChanger để tạo icon màu trắng với hiệu ứng isometric
        ColoredSVGButton.setup_button(
            self.calculator_button, 
            "assets/Icons/calculator.svg",
            icon_color=enabled.get("icon_color", "#ffffff"),
            icon_alpha=enabled.get("icon_alpha", 48),
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#121212"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )

        # Tạo BulletWidget từ config
        bullet_config = self.config['Widgets']['BulletWidget']
        self.bullet_widget = BulletWidget(self)
        
        self.bullet_widget.setGeometry(QtCore.QRect(
            bullet_config['x'], bullet_config['y'] + 34 - 10,  # Dịch lên 10px
            bullet_config['width'], bullet_config['height'])
        )

        self.retranslateUi()
        self.make_connection()
        # Khởi tạo trạng thái nút ban đầu
        self._update_action_buttons_state()
        # Khởi động timer để update dữ liệu liên tục
        self._data_timer = QtCore.QTimer()
        self._data_timer.timeout.connect(self.update_data)
        self._data_timer.start(100)  # 100ms, có thể chỉnh lại nếu muốn nhanh/chậm hơn

    def retranslateUi(self):
        pass  # No translation needed here

    def make_connection(self):
        self.ok_button.clicked.connect(self.on_ok_button_clicked)
        self.cancel_button.clicked.connect(self.on_cancel_button_clicked)
        self.launch_all_button.clicked.connect(self.on_launch_all_button_clicked)
        self.calculator_button.clicked.connect(self.on_calculator_button_clicked)

    def on_ok_button_clicked(self):
        """Xử lý sự kiện khi nhấn nút OK."""
        left_selected = self.bullet_widget.left_selected_launchers
        right_selected = self.bullet_widget.right_selected_launchers
        if not (left_selected or right_selected):
            # Chỉ log, không hiện popup
            from ui.views.event_log_tab import LogTab
            LogTab.log("Chưa chọn ống phóng nào!", "WARNING")
            return

        # Hiển thị widget xác nhận thay vì popup
        selected_count = len(left_selected) + len(right_selected)
        
        # Tạo confirmation widget nếu chưa có
        if not hasattr(self, 'confirmation_widget'):
            self.confirmation_widget = ConfirmationWidget(parent=self)
            self.confirmation_widget.setGeometry(0, 34, self.width(), self.height() - 34)
            self.confirmation_widget.confirmed.connect(self._execute_launch)
            self.confirmation_widget.cancelled.connect(self._cancel_launch)
        
        # Cập nhật geometry và hiển thị
        self.confirmation_widget.setGeometry(0, 34, self.width(), self.height() - 34)
        self.confirmation_widget.show_confirmation(
            "Xác nhận phóng",
            f"Bạn có chắc chắn phóng {selected_count} ống đã chọn?"
        )
    
    def _execute_launch(self):
        """Thực hiện phóng sau khi xác nhận."""
        left_selected = self.bullet_widget.left_selected_launchers.copy()
        right_selected = self.bullet_widget.right_selected_launchers.copy()
        selected_count = len(left_selected) + len(right_selected)
        
        # Cập nhật trạng thái các ống phóng đã chọn thành không sẵn sàng
        # new_left_status = self.bullet_widget.left_launcher_status.copy()
        # new_right_status = self.bullet_widget.right_launcher_status.copy()
        
        # for idx in left_selected:
        #     new_left_status[idx-1] = False
        # for idx in right_selected:
        #     new_right_status[idx-1] = False
            
        # Cập nhật trạng thái
        # self.bullet_widget._update_launcher_status("Giàn trái", new_left_status)
        # self.bullet_widget._update_launcher_status("Giàn phải", new_right_status)
        # config.AMMO_L = new_left_status
        # config.AMMO_R = new_right_status
        
        # Gửi lệnh qua CAN bus và kiểm tra kết quả
        can_success = True
        failed_can_data = []
        
        if len(left_selected) > 0:
            # Tạo CAN data cho giàn trái
            flags = [0]*18
            for i in left_selected:
                flags[i-1] = 1
            flag1 = int(''.join(str(b) for b in flags[:8][::-1]), 2)
            flag2 = int(''.join(str(b) for b in flags[8:16][::-1]), 2)
            flag3 = int(''.join(str(b) for b in flags[16:][::-1]), 2)
            can_data_left = [0x31, 0x31, flag1, flag2, flag3, 0x11]
            can_data_left_hex = ' '.join([f'0x{byte:02X}' for byte in can_data_left])
            
            if not sender_ammo_status(0x31, left_selected, CONFIG.IP_LEFT, CONFIG.SEND_PORT):
                can_success = False
                failed_can_data.append(f"Giàn trái: [{can_data_left_hex}]")
                
        if len(right_selected) > 0:
            # Tạo CAN data cho giàn phải
            flags = [0] * 18
            for i in right_selected:
                flags[i - 1] = 1
            flag1 = int(''.join(str(b) for b in flags[:8][::-1]), 2)
            flag2 = int(''.join(str(b) for b in flags[8:16][::-1]), 2)
            flag3 = int(''.join(str(b) for b in flags[16:][::-1]), 2)
            can_data_right = [0x31, 0x32, flag1, flag2, flag3, 0x11]
            can_data_right_hex = ' '.join([f'0x{byte:02X}' for byte in can_data_right])
            
            if not sender_ammo_status(0x32, right_selected, CONFIG.IP_RIGHT, CONFIG.SEND_PORT):
                can_success = False
                failed_can_data.append(f"Giàn phải: [{can_data_right_hex}]")
        
        # Ghi log và thông báo kết quả
        from ui.views.event_log_tab import LogTab
        
        if can_success:
            success_msg = f"Đã phóng thành công {selected_count} ống (Trái: {len(left_selected)}, Phải: {len(right_selected)})"
            LogTab.log(success_msg, "SUCCESS")
        else:
            failed_data_str = " | ".join(failed_can_data)
            warning_msg = f"Đã cập nhật trạng thái {selected_count} ống nhưng không thể gửi lệnh qua CAN bus - CAN Data: {failed_data_str} - ID: 0x29"
            LogTab.log(warning_msg, "WARNING")
        
        # Xóa danh sách đã chọn và cập nhật trạng thái nút sau khi phóng
        # self.bullet_widget.left_selected_launchers.clear()
        # self.bullet_widget.right_selected_launchers.clear()
        # self._update_action_buttons_state()
    
    def _cancel_launch(self):
        """Xử lý khi hủy phóng từ confirmation widget."""
        from ui.views.event_log_tab import LogTab
        LogTab.log("Đã hủy phóng!", "INFO")
        self.on_cancel_button_clicked()

    def on_cancel_button_clicked(self):
        """Xử lý sự kiện khi nhấn nút Cancel."""
        # Xóa danh sách các ống phóng đã chọn
        self.bullet_widget.left_selected_launchers.clear()
        self.bullet_widget.right_selected_launchers.clear()
        
        # Cập nhật lại giao diện
        self.bullet_widget._update_launcher_status("Giàn trái", 
                                                self.bullet_widget.left_launcher_status)
        self.bullet_widget._update_launcher_status("Giàn phải", 
                                                self.bullet_widget.right_launcher_status)
        
        # Cập nhật trạng thái nút
        self._update_action_buttons_state()

    def on_launch_all_button_clicked(self):
        """Xử lý sự kiện khi nhấn nút Launch All."""
        # Chọn tất cả các ống phóng sẵn sàng
        
        self.bullet_widget.left_selected_launchers.clear()
        self.bullet_widget.right_selected_launchers.clear()

        for idx in range(18):
            if self.bullet_widget.left_launcher_status[idx]:
                self.bullet_widget.left_selected_launchers.append(idx + 1)
            if self.bullet_widget.right_launcher_status[idx]:
                self.bullet_widget.right_selected_launchers.append(idx + 1)
        
        # Cập nhật giao diện để hiển thị các ống phóng đã chọn
        self.bullet_widget._update_launcher_status("Giàn trái", self.bullet_widget.left_launcher_status)
        self.bullet_widget._update_launcher_status("Giàn phải", self.bullet_widget.right_launcher_status)
        # Gọi hàm xử lý OK để phóng
        self.on_ok_button_clicked()

    def on_calculator_button_clicked(self):
        """Xử lý sự kiện khi nhấn nút Calculator."""
        # Nếu widget chưa được tạo, tạo mới
        if not hasattr(self, 'calculator_widget'):
            self.calculator_widget = BallisticCalculatorWidget(self)
            # Đặt widget chiếm toàn bộ diện tích của tab (không bị che bởi tab bar)
            self.calculator_widget.setGeometry(0, 34, self.width(), self.height() - 34)
            self.calculator_widget.raise_()  # Đưa lên trên cùng
            
            # Gán callback để cập nhật half-compass widgets khi áp dụng lượng sửa
            self.calculator_widget.on_angles_updated = self.update_half_compass_angles

        # Toggle hiển thị widget
        if self.calculator_widget.isVisible():
            self.calculator_widget.hide()
        else:
            # Cập nhật lại size khi hiển thị (trong trường hợp window bị resize)
            self.calculator_widget.setGeometry(0, 34, self.width(), self.height() - 34)

            # Cập nhật lại góc hiện tại trước khi hiển thị
            self.calculator_widget.current_elevation_left = config.ANGLE_L
            self.calculator_widget.current_direction_left = config.DIRECTION_L
            self.calculator_widget.current_elevation_right = config.ANGLE_R
            self.calculator_widget.current_direction_right = config.DIRECTION_R
            self.calculator_widget.update_angle_display()
            self.calculator_widget.show()

    def on_angle_input_clicked(self, side):
        """Xử lý sự kiện khi nhấn nút nhập khoảng cách và góc hướng.
        
        Args:
            side: 'left' hoặc 'right' để xác định giàn trái hay phải
        """
        # Lấy khoảng cách và hướng hiện tại tùy theo side
        if side == 'left':
            current_distance = config.DISTANCE_L
            current_direction = config.DIRECTION_L
            side_text = "Trái"
            idx = CAN_ID_ANGLE_LEFT  # ID cho giàn trái
        else:
            current_distance = config.DISTANCE_R
            current_direction = config.DIRECTION_R
            side_text = "Phải"
            idx = CAN_ID_ANGLE_RIGHT  # ID cho giàn phải
        
        # Tạo overlay dialog nếu chưa có hoặc tạo mới
        is_left = (side == 'left')
        if not hasattr(self, 'angle_input_dialog'):
            self.angle_input_dialog = AngleInputDialog(side_text, current_distance, current_direction, is_left, self)
            # Đặt overlay chiếm toàn bộ diện tích của tab
            self.angle_input_dialog.setGeometry(0, 34, self.width(), self.height() - 34)
            self.angle_input_dialog.raise_()  # Đưa lên trên cùng
        else:
            # Cập nhật giá trị hiện tại
            self.angle_input_dialog.side = side_text
            self.angle_input_dialog.is_left_side = is_left
            # Tải lại giới hạn và cập nhật validator khi chuyển bên
            self.angle_input_dialog.reload_limits_for_side()
            self.angle_input_dialog.distance_value = current_distance
            self.angle_input_dialog.direction_value = current_direction
            
            # Cập nhật toàn bộ UI theo trạng thái của bên hiện tại (khoảng cách vs góc tầm)
            # update_input_type_ui() sẽ tự động xóa và set đúng giá trị theo chế độ
            self.angle_input_dialog.update_input_type_label()
            self.angle_input_dialog.update_input_type_button()
            self.angle_input_dialog.update_input_type_ui()
            
            # Cập nhật góc hướng
            self.angle_input_dialog.direction_input.clear()
            if current_direction != 0:
                self.angle_input_dialog.direction_input.setText(str(current_direction))
            
            # Cập nhật label và button chế độ góc hướng
            self.angle_input_dialog.update_direction_mode_label()
            self.angle_input_dialog.update_direction_mode_button()
            # Cập nhật title
            title_label = self.angle_input_dialog.findChild(QLabel)
            if title_label and "Nhập góc" in title_label.text():
                title_label.setText(f"Nhập góc - Giàn {side_text}")
            # Cập nhật lại geometry trong trường hợp window bị resize
            self.angle_input_dialog.setGeometry(0, 34, self.width(), self.height() - 34)
            self.angle_input_dialog.raise_()
        
        # Disconnect tất cả signal cũ và kết nối lại với giá trị mới
        try:
            self.angle_input_dialog.accepted.disconnect()
        except:
            pass
        self.angle_input_dialog.accepted.connect(lambda: self._handle_angle_input_accepted(side, idx))
        
        # Hiển thị overlay
        self.angle_input_dialog.show()
        
    def _handle_angle_input_accepted(self, side, idx):
        """Xử lý khi người dùng xác nhận nhập khoảng cách và góc hướng."""
        # Lấy giá trị đã nhập
        input_value, direction, is_direct_elevation, use_high_table = self.angle_input_dialog.get_values()
        
        side_text = "Trái" if side == 'left' else "Phải"
        
        if is_direct_elevation:
            # Nhập góc tầm trực tiếp - không cần tính từ khoảng cách
            elevation = input_value
            
            # Tính khoảng cách từ góc tầm (nội suy ngược) và cập nhật lên giao diện
            interpolator = get_firing_table_interpolator()
            if interpolator:
                calculated_distance = interpolator.interpolate_range_from_angle(elevation)
                # Cập nhật khoảng cách vào config
                if side == 'left':
                    config.DISTANCE_L = calculated_distance
                else:
                    config.DISTANCE_R = calculated_distance
            
            # Cập nhật góc mục tiêu
            ip = CONFIG.IP_LEFT if side == 'left' else CONFIG.IP_RIGHT
            if side == 'left':
                config.AIM_ANGLE_L = elevation
                config.AIM_DIRECTION_L = direction
            else:
                config.AIM_ANGLE_R = elevation
                config.AIM_DIRECTION_R = direction
            
            # Gửi lệnh qua CAN bus
            from communication.data_sender import sender_angle_direction
            
            # Chuyển đổi sang int cho CAN bus
            elevation_int = int(elevation * 10)  # Nhân 10 để giữ 1 chữ số thập phân
            direction_int = int(direction * 10)  # Nhân 10 để giữ 1 chữ số thập phân
            
            # Gửi lệnh với idx tương ứng
            sender_angle_direction(elevation_int, direction_int, idx, ip, CONFIG.SEND_PORT)
            
            # Log
            from ui.views.event_log_tab import LogTab
            if interpolator:
                LogTab.log(f"Đã nhập góc tầm trực tiếp {elevation:.1f}° (khoảng cách ~{calculated_distance:.2f}m) và góc hướng {direction:.1f}° cho giàn {side_text}", "INFO")
            else:
                LogTab.log(f"Đã nhập góc tầm trực tiếp {elevation:.1f}° và góc hướng {direction:.1f}° cho giàn {side_text}", "INFO")
        else:
            # Nhập khoảng cách - tính toán góc tầm từ bảng bắn
            distance = input_value
            
            # Lưu thông tin bảng bắn được sử dụng
            if side == 'left':
                config.USE_HIGH_TABLE_L = use_high_table
            else:
                config.USE_HIGH_TABLE_R = use_high_table
            
            # Cập nhật khoảng cách vào config (chỉ khi ở chế độ thủ công)
            if side == 'left':
                if not config.DISTANCE_MODE_AUTO_L:  # Chỉ cập nhật khi ở chế độ thủ công
                    config.DISTANCE_L = distance
            else:
                if not config.DISTANCE_MODE_AUTO_R:  # Chỉ cập nhật khi ở chế độ thủ công
                    config.DISTANCE_R = distance
            
            # Chọn bảng bắn dựa trên lựa chọn của người dùng (chỉ khi khoảng cách >= 9100)
            if use_high_table and distance >= 9100:
                interpolator = load_firing_table("table1_high.csv")
                table_name = "bảng bắn cao"
            else:
                interpolator = get_firing_table_interpolator()
                table_name = "bảng bắn thấp"
            
            if interpolator:
                elevation = interpolator.interpolate_angle(distance)
                
                # Cập nhật góc mục tiêu
                if side == 'left':
                    config.AIM_ANGLE_L = elevation
                    config.AIM_DIRECTION_L = direction
                else:
                    config.AIM_ANGLE_R = elevation
                    config.AIM_DIRECTION_R = direction
                
                # Gửi lệnh qua CAN bus
                from communication.data_sender import sender_angle_direction
                
                # Chuyển đổi sang int cho CAN bus
                elevation_int = int(elevation * 10)  # Nhân 10 để giữ 1 chữ số thập phân
                direction_int = int(direction * 10)  # Nhân 10 để giữ 1 chữ số thập phân
                # Gửi lệnh với idx tương ứng
                sender_angle_direction(elevation_int, direction_int, idx)
                
                # Log thông tin bảng bắn được sử dụng
                from ui.views.event_log_tab import LogTab
                if distance >= 9100:
                    LogTab.log(f"Sử dụng {table_name} cho khoảng cách {distance:.1f}m - Góc tầm: {elevation:.1f}°", "INFO")
            else:
                from ui.views.event_log_tab import LogTab
                LogTab.log(f"Không thể tính toán góc tầm - bảng bắn chưa được tải", "ERROR")
                # Bỏ popup, chỉ log

    def update_half_compass_angles(self, corrections):
        """Lưu lượng sửa từ ballistic calculator - sẽ được áp dụng trong update_data()."""
        # Chỉ lưu lượng sửa, không thay đổi config
        self.elevation_correction_left = corrections['elevation_correction_left']
        self.elevation_correction_right = corrections['elevation_correction_right']
        self.direction_correction_left = corrections['direction_correction_left']
        self.direction_correction_right = corrections['direction_correction_right']
        
        # Lượng sửa sẽ được áp dụng tự động trong update_data()

    def _update_action_buttons_state(self):
        """Cập nhật trạng thái và giao diện của OK Button và Cancel Button dựa trên việc có nút nào được chọn."""
        has_selection = (len(self.bullet_widget.left_selected_launchers) > 0 or 
                         len(self.bullet_widget.right_selected_launchers) > 0)
        btn_colors = self.config.get('ButtonColors', {})

        # Kiểm tra có ống phóng nào sẵn sàng không (cho Launch All button)
        has_ready_launchers = (any(self.bullet_widget.left_launcher_status) or 
                               any(self.bullet_widget.right_launcher_status))

        # Luôn cập nhật OK Button và Cancel Button với màu mới từ config
        if has_selection:
            # Có nút được chọn - sử dụng màu enabled thay vì selected
            enabled = btn_colors.get('enabled', {})
            ColoredSVGButton.setup_button(
                self.ok_button, 
                "assets/Icons/launch.svg",
                icon_color=enabled.get("icon_color", "#000000"),
                icon_alpha=255,  # Icon không mờ khi enabled
                icon_size=(80, 80),
                top_color=enabled.get("top_color", "#ffffff"),
                border_color=enabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            ColoredSVGButton.setup_button(
                self.cancel_button, 
                "assets/Icons/cancel.svg",
                icon_color=enabled.get("icon_color", "#000000"),
                icon_alpha=255,  # Icon không mờ khi enabled
                icon_size=(80, 80),
                top_color=enabled.get("top_color", "#ffffff"),
                border_color=enabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            # Tăng độ cao isometric gấp đôi (từ 6 lên 12)
            self.ok_button.offset_y = 12
            self.cancel_button.offset_y = 12
            # Bật chức năng bấm
            self.ok_button.setEnabled(True)
            self.cancel_button.setEnabled(True)
        else:
            # Không có nút nào được chọn - nút màu đen, SVG màu trắng, độ cao isometric bình thường
            disabled = btn_colors.get('disabled', {})
            ColoredSVGButton.setup_button(
                self.ok_button, 
                "assets/Icons/launch.svg",
                icon_color=disabled.get("icon_color", "#ffffff"),
                icon_alpha=disabled.get("icon_alpha", 48),
                icon_size=(80, 80),
                top_color=disabled.get("top_color", "#121212"),
                border_color=disabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            ColoredSVGButton.setup_button(
                self.cancel_button, 
                "assets/Icons/cancel.svg",
                icon_color=disabled.get("icon_color", "#ffffff"),
                icon_alpha=disabled.get("icon_alpha", 48),
                icon_size=(80, 80),
                top_color=disabled.get("top_color", "#121212"),
                border_color=disabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            # Khôi phục độ cao isometric ban đầu
            self.ok_button.offset_y = 6
            self.cancel_button.offset_y = 6
            # Tắt chức năng bấm
            self.ok_button.setEnabled(False)
            self.cancel_button.setEnabled(False)

        # Luôn cập nhật Launch All Button với màu mới từ config
        if has_ready_launchers:
            enabled = btn_colors.get('enabled', {})
            ColoredSVGButton.setup_button(
                self.launch_all_button, 
                "assets/Icons/launch_all.svg",
                icon_color=enabled.get("icon_color", "#000000"),
                icon_alpha=255,  # Icon không mờ khi enabled
                icon_size=(80, 80),
                top_color=enabled.get("top_color", "#ffffff"),
                border_color=enabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            self.launch_all_button.offset_y = 12
            self.launch_all_button.setEnabled(True)
        else:
            disabled = btn_colors.get('disabled', {})
            ColoredSVGButton.setup_button(
                self.launch_all_button, 
                "assets/Icons/launch_all.svg",
                icon_color=disabled.get("icon_color", "#ffffff"),
                icon_alpha=disabled.get("icon_alpha", 48),
                icon_size=(80, 80),
                top_color=disabled.get("top_color", "#121212"),
                border_color=disabled.get("border_color", "#30ffffff"),
                border_radius=8,
                isometric=True
            )
            self.launch_all_button.offset_y = 6
            self.launch_all_button.setEnabled(False)

        # Calculator Button luôn luôn enabled với màu enabled
        enabled = btn_colors.get('enabled', {})
        ColoredSVGButton.setup_button(
            self.calculator_button, 
            "assets/Icons/calculator.svg",
            icon_color=enabled.get("icon_color", "#000000"),
            icon_alpha=255,  # Icon không mờ khi enabled
            icon_size=(80, 80),
            top_color=enabled.get("top_color", "#ffffff"),
            border_color=enabled.get("border_color", "#30ffffff"),
            border_radius=8,
            isometric=True
        )
        self.calculator_button.offset_y = 12
        self.calculator_button.setEnabled(True)

        # Trigger repaint cho tất cả button
        self.ok_button.update()
        self.cancel_button.update()
        self.launch_all_button.update()
        self.calculator_button.update()

    def update_data(self):
        """Cập nhật các thông số, trang thái của các ống phóng và góc hướng hiện tại
        và góc tính toán từ hệ thống điều khiển bắn.
        """
        # Tính toán góc tầm MỤC TIÊU liên tục từ khoảng cách hiện tại
        # Chỉ cập nhật khi đang ở chế độ nhập khoảng cách (không nhập góc tầm trực tiếp)
        
        # AIM_ANGLE = góc mục tiêu (từ nội suy bảng bắn)
        # Chỉ cập nhật tự động khi đang ở chế độ nhập khoảng cách
        if config.ELEVATION_INPUT_FROM_DISTANCE_L:
            # Chọn bảng bắn dựa trên USE_HIGH_TABLE_L
            if config.USE_HIGH_TABLE_L and config.DISTANCE_L >= 9100:
                interpolator_l = load_firing_table("table1_high.csv")
            else:
                interpolator_l = get_firing_table_interpolator()
            
            if interpolator_l:
                config.AIM_ANGLE_L = interpolator_l.interpolate_angle(config.DISTANCE_L)
        
        if config.ELEVATION_INPUT_FROM_DISTANCE_R:
            # Chọn bảng bắn dựa trên USE_HIGH_TABLE_R
            if config.USE_HIGH_TABLE_R and config.DISTANCE_R >= 9100:
                interpolator_r = load_firing_table("table1_high.csv")
            else:
                interpolator_r = get_firing_table_interpolator()
            
            if interpolator_r:
                config.AIM_ANGLE_R = interpolator_r.interpolate_angle(config.DISTANCE_R)
        
        # AIM_DIRECTION_L/R = hướng mục tiêu (được set từ targeting hoặc ballistic calculator)
        # KHÔNG tự động cập nhật ở đây - chỉ được set khi có tính toán mục tiêu
        # ANGLE_L/R và DIRECTION_L/R = góc/hướng HIỆN TẠI từ cảm biến (CAN bus)
        # Sẽ được cập nhật từ data_receiver khi nhận CAN bus 0x200, 0x201
        
        self.bullet_widget._update_launcher_status("Giàn trái", config.AMMO_L)
        self.bullet_widget._update_launcher_status("Giàn phải", config.AMMO_R)
        
        # Cập nhật trạng thái của OK Button và Cancel Button
        self._update_action_buttons_state()
        w_direction = random.randint(30,60)  # Giả lập hướng của tàu so với địa lý (độ, 0 = Bắc)
        # config.DISTANCE_L = random.uniform(4000, 5000)  # Giả lập khoảng cách đến mục tiêu (m)
        # DIRECTION_L/R = hướng hiện tại, AIM_DIRECTION_L/R = hướng mục tiêu
        # Áp dụng lượng sửa vào hướng mục tiêu hiển thị
        self.compass_left.update_angle(
            aim_direction=config.AIM_DIRECTION_L + self.direction_correction_left, 
            current_direction=config.DIRECTION_L, 
            w_direction=config.W_DIRECTION
        )
        self.compass_right.update_angle(
            aim_direction=config.AIM_DIRECTION_R + self.direction_correction_right, 
            current_direction=config.DIRECTION_R, 
            w_direction=config.W_DIRECTION
        )
        # self.compass_left.update_angle(aim_direction=-70, current_direction=-100, w_direction=config.W_DIRECTION)
        # self.compass_right.update_angle(aim_direction=90, current_direction=90, w_direction=w_direction)
        
        # ANGLE_L/R = góc hiện tại từ cảm biến, AIM_ANGLE_L/R = góc mục tiêu từ nội suy
        # Áp dụng lượng sửa (nếu có) vào góc mục tiêu hiển thị
        self.half_compass_left.update_angle(
            current_angle=config.ANGLE_L, 
            aim_angle=config.AIM_ANGLE_L + self.elevation_correction_left, 
            current_direction=config.DIRECTION_L, 
            aim_direction=config.AIM_DIRECTION_L + self.direction_correction_left
        )
        self.half_compass_right.update_angle(
            current_angle=config.ANGLE_R, 
            aim_angle=config.AIM_ANGLE_R + self.elevation_correction_right, 
            current_direction=config.DIRECTION_R, 
            aim_direction=config.AIM_DIRECTION_R + self.direction_correction_right
        )
        # self.half_compass_left.update_angle(current_angle=15, aim_angle=15,
        #                                     current_direction=45, aim_direction=16)
        # self.half_compass_right.update_angle(current_angle=45, aim_angle=45,
        #                                      current_direction=45, aim_direction=45)
        
        # Tính góc mục tiêu sau khi áp dụng lượng sửa (để hiển thị trong numeric display)
        aim_angle_left_corrected = config.AIM_ANGLE_L + self.elevation_correction_left
        aim_angle_right_corrected = config.AIM_ANGLE_R + self.elevation_correction_right
        aim_direction_left_corrected = config.AIM_DIRECTION_L + self.direction_correction_left
        aim_direction_right_corrected = config.AIM_DIRECTION_R + self.direction_correction_right
        
        # Tạo text hiển thị chế độ
        mode_text_l = "AUTO" if config.DISTANCE_MODE_AUTO_L else "MANUAL"
        mode_text_r = "AUTO" if config.DISTANCE_MODE_AUTO_R else "MANUAL"
        
        self.numeric_data_widget.update_data(
            **{
                "Hướng ngắm hiện tại (độ)": (f"{config.DIRECTION_L:.1f}", f"{config.DIRECTION_R:.1f}"),
                "Hướng ngắm mục tiêu (độ)": (f"{aim_direction_left_corrected:.1f}", f"{aim_direction_right_corrected:.1f}"),
                "Góc tầm hiện tại (độ)": (f"{config.ANGLE_L:.1f}", f"{config.ANGLE_R:.1f}"),
                "Góc tầm mục tiêu (độ)": (f"{aim_angle_left_corrected:.1f}", f"{aim_angle_right_corrected:.1f}"),
                "Pháo sẵn sàng": (str(sum(self.bullet_widget.left_launcher_status)), str(sum(self.bullet_widget.right_launcher_status))),
                "Pháo đã chọn": (str(len(self.bullet_widget.left_selected_launchers)), str(len(self.bullet_widget.right_selected_launchers))),
                "Khoảng cách (m)": (f"{config.DISTANCE_L:.2f}", f"{config.DISTANCE_R:.2f}"),
                "Chế độ K/C": (mode_text_l, mode_text_r)
            }
        )
