#-*- coding: utf-8 -*-


from PyQt5.QtWidgets import QWidget, QLabel, QPushButton
from PyQt5.QtGui import QFont, QPainter, QPen, QColor, QLinearGradient, QRadialGradient, QBrush
from PyQt5.QtCore import Qt, QRect, QPropertyAnimation, QEasingCurve, QRectF, QPointF, pyqtProperty
from PyQt5.QtWidgets import QGraphicsOpacityEffect
from ...ui_config import NUMBER_LIST
import yaml
import os

# Load button colors from config.yaml
def load_button_colors():
    config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '..', 'config.yaml')
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config.get('ButtonColors', {})
    except Exception:
        return {}

BUTTON_COLORS = load_button_colors()

def reload_button_colors():
    """Reload button colors from config.yaml"""
    global BUTTON_COLORS
    BUTTON_COLORS = load_button_colors()
    return BUTTON_COLORS

from ..components.buttons.isometric import BulletIsometricButton


class BulletWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Khởi tạo trạng thái
        self.left_launcher_status = [True for i in range(18)]
        self.right_launcher_status = [True for i in range(18)]
        self.left_selected_launchers = []
        self.right_selected_launchers = []
        self.numeric_data_widget = None
        
        # Tạo giao diện
        self._create_launcher_frame("Giàn trái", 10, 15, self.left_launcher_status)
        self._create_launcher_frame("Giàn phải", 630, 15, self.right_launcher_status)

    def _set_numeric_data_widget(self, widget: QWidget) -> None:
        """Khi thông số thay đổi sẽ tham chiếu đến numeric data object để cập nhật dữ liệu

        Args:
            widget (QWidget): NumericData Widget

        Returns:
            None
        """
        self.numeric_data_widget = widget

    def _update_numeric_display(self) -> None:
        """Cập nhật lại thông số hiển thị trên NumericData Widget

        Returns:
            None
        """
        if self.numeric_data_widget:
            # Count available missiles
            left_available = sum(1 for status in self.left_launcher_status if status)
            right_available = sum(1 for status in self.right_launcher_status if status)
            
            # Count selected missiles
            left_selected = len(self.left_selected_launchers)
            right_selected = len(self.right_selected_launchers)
            
            # Cập nhật dữ liệu với đúng key name
            self.numeric_data_widget.update_data(**{
                "Available Missiles": (str(left_available), str(right_available)),
                "Selected Missiles": (str(left_selected), str(right_selected))
            })

    def _create_launcher_frame(self, title: str, x: int, y: int, launcher_status: list) -> None:
        """Tạo frame chứa các nút bấm cho launcher

        Args:
            title (str): Tên giàn phóng.
            x (int): Tọa độ trục x.
            y (int): Tọa độ trục y.
            launcher_status (list): Trạng thái khởi tạo (Ống phóng sẵn sàng thì có trạng thái là True hoặc 1 ngược lại là 0/False)
        
        Returns: 
            None
        """        
        # Tạo frame background
        frame_label = QLabel(self)
        frame_label.setGeometry(QRect(x, y, 590, 320))
        frame_label.setStyleSheet("""
            background-color: #121212;
            border-radius: 20px;
            border: 2px solid #404040;
        """)

        # Tạo tiêu đề
        title_label = QLabel(self)
        title_label.setGeometry(QRect(x, y, 590, 34))  # Tăng chiều cao tiêu đề
        title_label.setFont(QFont("Tahoma", 22, QFont.Bold))  # Tăng cỡ chữ
        title_label.setStyleSheet("""
            background-color: #404040;
            color: #ffffff;
            font-size: 20px;
            border-top-left-radius: 20px;
            border-top-right-radius: 20px;
            border-bottom: 2px solid #606060;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setText(title)

        # Tạo nút chỉ thị trạng thái
        # status_button = QPushButton(self)
        # status_button.setGeometry(QRect(x + 40, y + 5, 20, 20))
        # status_button.setStyleSheet("""
        #     background-color: #ffffff;
        #     border-radius: 10px;
        #     border: 2px solid #d0d0d0;
        # """)

        # Tạo các nút ống phóng
        self._create_launcher_buttons(x, y, title, launcher_status)

    def _create_launcher_buttons(self, base_x: int, base_y: int, launcher_side: str, launcher_status: list) -> None:
        # Sắp xếp theo NUMBER_LIST từ config.py (3 hàng 6 cột)
        button_size = 70
        cols = 6  # 6 cột theo NUMBER_LIST
        rows = 3  # 3 hàng theo NUMBER_LIST
        h_space = (590 - cols * button_size) // (cols + 1)  # 590 là chiều rộng frame
        v_space = (320 - 30 - rows * button_size) // (rows + 1)  # 320 là chiều cao frame, 30 là tiêu đề
        
        # Tạo nút theo vị trí trong NUMBER_LIST
        for row_idx, row in enumerate(NUMBER_LIST):
            for col_idx, number in enumerate(row):
                x = base_x + h_space + col_idx * (button_size + h_space)
                y = base_y + 30 + v_space + row_idx * (button_size + v_space)
                button = BulletIsometricButton(str(number), self)
                button.setGeometry(QRect(x, y, button_size, button_size))
                button.set_state(launcher_status[number-1], False)
                button.setObjectName(f"{launcher_side}_{number}")
                button.clicked.connect(
                    lambda checked, side=launcher_side, index=number: 
                    self._on_button_clicked(side, index)
                )

    def _on_button_clicked(self, launcher_side: str, button_index: int) -> None:
        """Xử lý sự kiện khi nút được nhấn.

        Args:
            launcher_side (str): Tên/Vị trí giàn phóng (Giàn trái hoặc Giàn phải)
            button_index (int): Vị trí của giàn phóng.

        Returns:
            None
        """
        selected_list = (self.left_selected_launchers if launcher_side == "Giàn trái" 
                        else self.right_selected_launchers)
        status_list = (self.left_launcher_status if launcher_side == "Giàn trái" 
                      else self.right_launcher_status)

        # Chỉ xử lý khi ống phóng sẵn sàng
        if status_list[button_index-1]:
            if button_index in selected_list:
                selected_list.remove(button_index)
            else:
                selected_list.append(button_index)

            button = self.findChild(BulletIsometricButton, f"{launcher_side}_{button_index}")
            # Cập nhật trạng thái
            self._update_button_style(button, status_list[button_index-1], 
                                    button_index in selected_list)
            
            # Đảm bảo cập nhật numeric display sau khi click
            self._update_numeric_display()

    def _update_button_style(self, button: BulletIsometricButton, is_ready: bool, is_selected: bool) -> None:
        """Cập nhật trạng thái và màu sắc của nút bấm với hiệu ứng isometric 3D.

        Args:
            button (IsometricButton): IsometricButton object.
            is_ready (bool): Trạng thái của ống phóng (ready or not).
            is_selected (bool): Ống phóng đã chọn hay chưa.

        Returns:
            None
        """        
        if button:
            button.set_state(is_ready, is_selected)
            button.setEnabled(is_ready)

    def _update_launcher_status(self, launcher_side: str, new_status: list) -> None:
        """Cập nhật tráng thái của giàn phóng.

        Args:
            launcher_side (str): Tên/Vị trí giàn phóng
            new_status (list): Trạng thái mới của giàn phóng.

        Returns:
            None
        """
        if len(new_status) != 18:
            print(f"Error: Cần đúng 18 trạng thái, nhưng nhận được {len(new_status)}")
            return

        # Cập nhật trạng thái và kiểm tra danh sách đã chọn
        if launcher_side == "Giàn trái":
            self.left_launcher_status = new_status
            # Chỉ giữ lại các ống phóng đã chọn và vẫn sẵn sàng
            self.left_selected_launchers = [
                idx for idx in self.left_selected_launchers 
                if new_status[idx-1]
            ]
        
        else:
            self.right_launcher_status = new_status
            # Chỉ giữ lại các ống phóng đã chọn và vẫn sẵn sàng
            self.right_selected_launchers = [
                idx for idx in self.right_selected_launchers 
                if new_status[idx-1]    
            ]
            

        # Cập nhật giao diện các nút theo NUMBER_LIST
        for row_idx, row in enumerate(NUMBER_LIST):
            for col_idx, number in enumerate(row):
                button = self.findChild(BulletIsometricButton, f"{launcher_side}_{number}")
                if button:
                    is_selected = (number in self.left_selected_launchers if launcher_side == "Giàn trái"
                                 else number in self.right_selected_launchers)
                    
                    self._update_button_style(
                        button,
                        new_status[number-1],
                        is_selected
                    )
                    # Cập nhật trạng thái enabled của nút
                    button.setEnabled(new_status[number-1])
        # Đảm bảo cập nhật numeric display sau khi thay đổi trạng thái
        self._update_numeric_display()

    def update_button_colors(self):
        """Cập nhật màu sắc của tất cả các nút từ config mới"""
        reload_button_colors()  # Reload global config
        
        # Cập nhật lại tất cả các nút
        for row_idx, row in enumerate(NUMBER_LIST):
            for col_idx, number in enumerate(row):
                # Cập nhật nút trái
                left_button = self.findChild(BulletIsometricButton, f"Giàn trái_{number}")
                if left_button:
                    left_button.refresh_colors()  # Refresh colors for this button
                    is_selected = number in self.left_selected_launchers
                    left_button.set_state(self.left_launcher_status[number-1], is_selected)
                    left_button.update()  # Force repaint
                    left_button.repaint()  # Force immediate repaint
                
                # Cập nhật nút phải
                right_button = self.findChild(BulletIsometricButton, f"Giàn phải_{number}")
                if right_button:
                    right_button.refresh_colors()  # Refresh colors for this button
                    is_selected = number in self.right_selected_launchers
                    right_button.set_state(self.right_launcher_status[number-1], is_selected)
                    right_button.update()  # Force repaint
                    right_button.repaint()  # Force immediate repaint

    def update(self, left_status: list = [False] * 18, right_status: list = [False] * 18) -> None:
        """Cập nhật trạng thái của giàn phóng trái và phải khi có thay đổi

        Args:
            left_status (list): Trạng thái giàn trái. Defaults to [False] * 18.
            right_status (list): Trạng thái giàn phải. Defaults to [False] * 18.

        Example:
            left_status = [True] * 18
            right_status = [False] * 18

        Returns:
            None
        """
        
        if len(left_status) != 18 or len(right_status) != 18:
            raise ValueError("Cần đúng 18 trạng thái cho cả giàn trái và phải")

        # new_left_status = [not status for status in self.left_launcher_status]
        self._update_launcher_status("Giàn trái", left_status)
        
        # new_right_status = [not status for status in self.right_launcher_status]
        self._update_launcher_status("Giàn phải", right_status)