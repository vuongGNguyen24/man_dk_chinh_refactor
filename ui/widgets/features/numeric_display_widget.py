#-*- coding: utf-8 -*-
from typing import Dict, Literal
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QBrush, QColor, QPen, QFont, QTextOption
from PyQt5.QtCore import Qt, QRectF, QLineF

class NumericDataWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.data = {
            "Góc hướng hiện tại (độ)": ["0", "0"],
            "Góc hướng mục tiêu (độ)": ["0", "0"],
            "Góc tầm hiện tại (độ)": ["0", "0"],
            "Góc tầm mục tiêu (độ)": ["0", "0"],
            "Pháo sẵn sàng": ["0", "0"],
            "Pháo đã chọn": ["0", "0"],
            "Khoảng cách (m)": ["0", "0"],
        }

    def get_data(self, side:Literal["left", "right"], key: str) -> str:
        """

        Lấy thông tin hiện tại từ bảng thông số

        Args:
            side (Literal[&quot;left&quot;, &quot;right&quot;]): giàn trái hay giàn phải
            key (str): tên thông số

        Returns:
            str: thông số hiện tại dạng string

        Raises:
            ValueError: thông số không tồn tại
        """
        if key not in self.data:
            raise ValueError(f"Không tìm thấy thông số {key}")
        
        index = 0 if side == "left" else 1
        return self.data[key][index]
    
    def update_data_on_launcher(self, side: Literal["left", "right"], **kwargs: Dict[str, float]) -> None:
        """
        Cập nhật dữ liệu cho bảng thông số của một giàn. Cho phép cập nhật từng trường riêng lẻ.
        
        Args:
            side (Literal[&quot;left&quot;, &quot;right&quot;]): giàn trái hay giàn phải
            **kwargs: Các cặp key-value cần cập nhật
                Các key hợp lệ:
                - "Current Direction": tuple(str, str)
                - "Aim Direction": tuple(str, str)
                - "Current Angle": tuple(str, str)
                - "Aim Angle": tuple(str, str)
                - "Available Missiles": tuple(str, str)
                - "Selected Missiles": tuple(str, str)
                - "Distance": tuple(str, str)
        
        Returns:
            None
        """
        index = 0 if side == "left" else 1
        data = self.data
        for key, value in kwargs.items():
            if key in data:  
                data[key][index] = value
            else:
                raise ValueError(f"Không tìm thấy thông số {key}")
            
    def update_data(self, **kwargs) -> None:
        """
        Cập nhật dữ liệu cho bảng thông số. Cho phép cập nhật từng trường riêng lẻ.
        
        Args:
            **kwargs: Các cặp key-value cần cập nhật
                Các key hợp lệ:
                - "Current Direction": tuple(str, str)
                - "Aim Direction": tuple(str, str)
                - "Current Angle": tuple(str, str)
                - "Aim Angle": tuple(str, str)
                - "Available Missiles": tuple(str, str)
                - "Selected Missiles": tuple(str, str)
                - "Distance": tuple(str, str)
        
        Example:
            widget.update_data(
                Current_Direction=("30°", "45°"),
                Available_Missiles=("5", "7")
            )
        Returns:
            None
        """
        # Cập nhật các trường được chỉ định
        for key, value in kwargs.items():
            if key in self.data:  # Loại bỏ replace("_", " ")
                if isinstance(value, list) and len(value) == 2:
                    self.data[key] = value
                    # print(f"Updated {key}: {value}")  # Debug print
                else:
                    print(f"Warning: Invalid value for {key}. Need tuple with 2 elements.")
    
        # Force repaint
        self.update()


    def paintEvent(self, event: QWidget.event) -> None:
        """Xử lý sự kiện vẽ cho widget.

        Args:
            event (Qwidget.event): The paint event object.
        
        Returns:
            None
        """

        size = min(self.width(), self.height())

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Vùng vẽ
        rect = self.rect().adjusted(10, 10, -20, -10)

        # Nền đen, viền và chữ màu trắng 95% đen 5%
        white_95 = QColor(242, 242, 242)  # 95% trắng
        black_5 = QColor(13, 13, 13)      # 5% đen
        mixed_white = QColor(
            int(0.95 * 255 + 0.05 * 0),
            int(0.95 * 255 + 0.05 * 0),
            int(0.95 * 255 + 0.05 * 0)
        )
        mixed_black = QColor(
            int(0.05 * 255 + 0.95 * 0),
            int(0.05 * 255 + 0.95 * 0),
            int(0.05 * 255 + 0.95 * 0)
        )
        painter.setBrush(QBrush(QColor(18, 18, 18)))  # Nền #121212
        painter.setPen(QPen(mixed_white, 5))  # Viền trắng 95% đen 5%
        painter.drawRoundedRect(rect, 20, 20)

        # Font chữ phù hợp tiếng Việt, màu trắng 95% đen 5%
        font = QFont("DejaVu Sans", 12, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QPen(mixed_white, 4))

        # Tính lại row_height dựa trên số dòng thực tế để không bị tràn
        num_rows = len(self.data) + 1  # +1 cho header
        row_height = rect.height() // num_rows

        # Tính lại vị trí và chiều rộng các cột cho đúng yêu cầu, đảm bảo không tràn chữ
        col_width = int(rect.width() * 0.225)
        col_key_width = rect.width() - 2 * col_width
        x_left = rect.left()
        x_key = x_left + col_width
        x_right = x_key + col_key_width
        y = rect.top()
        option = QTextOption()
        option.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
        # Header
        rect = QRectF(x_left, y, col_width, row_height)
        painter.drawText(rect, "Trái", option)
        
        rect = QRectF(x_key, y, col_key_width, row_height)
        painter.drawText(rect, "Thông số", option)
        
        rect = QRectF(x_right, y, col_width, row_height)
        painter.drawText(rect, "Phải", option)
        y += row_height

        # Đường kẻ dọc giữa các cột màu trắng 95% đen 5%
        painter.setPen(QPen(mixed_white, 2))
        
        line = QLineF(x_key, rect.top(), x_key, rect.bottom())
        painter.drawLine(line)
        
        line = QLineF(x_right, rect.top(), x_right, rect.bottom())
        painter.drawLine(line)
        painter.setPen(QPen(mixed_white, 5))

        # Nội dung bảng
        for idx, (key, (left_val, right_val)) in enumerate(self.data.items()):
            painter.drawText(QRectF(x_left, y, col_width, row_height), int(Qt.AlignVCenter | Qt.AlignHCenter), str(left_val))
            painter.drawText(QRectF(x_key, y, col_key_width, row_height), int(Qt.AlignVCenter | Qt.AlignHCenter), key)
            painter.drawText(QRectF(x_right, y, col_width, row_height), int(Qt.AlignVCenter | Qt.AlignHCenter), str(right_val))
            if idx < len(self.data) - 1:
                pen = QPen(mixed_white, 1, Qt.DashLine)
                painter.setPen(pen)
                y_line = y + row_height
                painter.drawLine(
                    int(self.rect().left() + 35),
                    int(y_line),
                    int(self.rect().right() - 40),
                    int(y_line)
                )
                painter.setPen(QPen(mixed_white, 5)) 	
            y += row_height
