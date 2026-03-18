# -*- coding: utf-8 -*-

import math, os, sys

from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPainter, QPen, QColor, QPixmap
from PyQt5.QtCore import Qt, QPointF, QRectF, QTimer, pyqtProperty, QPropertyAnimation, QEasingCurve


class AngleCompass(QWidget):

    def __init__(self, aim_direction: float, current_direction: float, redlines: list = None, w_direction: float = 0, parent=None):
        """Khởi tạo widget đồng hồ chỉ hướng với góc hiện tại và góc mục tiêu.

        Args:
            aim_direction (float): Góc cột ngắm.
            current_direction (float): Góc giàn bắn.
            redlines (list): Danh sách góc compass để vẽ vùng cấm (0° = Bắc/trên, tăng theo chiều kim đồng hồ).
            w_direction (float): Hướng của tàu so với địa lý (độ, 0 = Bắc).
            parent (QWidget, optional): _description_. Defaults to None.
        """
        super().__init__(parent)
        self._aim_direction = aim_direction  # Default aim_direction
        self._current_direction = current_direction  # Default current_direction
        self.redlines = redlines or [210, 360]  # Mặc định nếu không truyền vào (góc compass)
        self._w_direction = w_direction  # Hướng địa lý
        self.static_pixmap = None
        self._aim_anim = QPropertyAnimation(self, b"aimDirection")
        self._current_anim = QPropertyAnimation(self, b"currentDirection")
        self._w_anim = QPropertyAnimation(self, b"wDirection")
        self._aim_anim.setDuration(500)
        self._current_anim.setDuration(500)
        self._w_anim.setDuration(300)  # Animation nhanh hơn cho w_direction
        self._aim_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._current_anim.setEasingCurve(QEasingCurve.InOutQuad)
        self._w_anim.setEasingCurve(QEasingCurve.InOutQuad)
        
        # Animation cho missile
        self.missile_position = 0.0  # Vị trí của missile trên đường parabol (0.0 -> 1.0)
        self.missile_timer = QTimer()
        self.missile_timer.timeout.connect(self._update_missile_position)
        self.missile_timer.start(50)  # Cập nhật mỗi 50ms

    def getAimDirection(self):
        return self._aim_direction
    def setAimDirection(self, value):
        self._aim_direction = value
        self.update()
    aimDirection = pyqtProperty(float, fget=getAimDirection, fset=setAimDirection)

    def getCurrentDirection(self):
        return self._current_direction
    def setCurrentDirection(self, value):
        self._current_direction = value
        self.update()
    currentDirection = pyqtProperty(float, fget=getCurrentDirection, fset=setCurrentDirection)

    def getWDirection(self):
        return self._w_direction
    def setWDirection(self, value):
        self._w_direction = value
        self.update()
    wDirection = pyqtProperty(float, fget=getWDirection, fset=setWDirection)

    def update_angle(self, aim_direction: float = 0, current_direction: float = 0, w_direction: float = None) -> None:
        """Cập nhật góc hiện tại và góc mục tiêu - TẮT ANIMATION để tránh lỗi."""
        # Update trực tiếp không qua animation
        if self._aim_direction != aim_direction:
            self.setAimDirection(aim_direction)
        
        if self._current_direction != current_direction:
            self.setCurrentDirection(current_direction)
        
        if w_direction is not None and self._w_direction != w_direction:
            self.setWDirection(w_direction)
        
    def _update_missile_position(self):
        """Cập nhật vị trí missile trên đường parabol."""
        self.missile_position += 0.03  # Tăng 3% mỗi lần cập nhật
        if self.missile_position > 1.0:
            self.missile_position = 0.0  # Reset về đầu đường parabol
        self.update()  # Yêu cầu vẽ lại widget
        
    def resizeEvent(self, event):
        """Vẽ lại giao diện tĩnh khi kích thước thay đổi."""
        # Only create static pixmap when widget has a valid size
        w = max(0, self.width())
        h = max(0, self.height())
        if w <= 0 or h <= 0:
            self.static_pixmap = None
            return

        self.static_pixmap = QPixmap(w, h)
        self.static_pixmap.fill(Qt.transparent)
        painter = QPainter()
        if not painter.begin(self.static_pixmap):
            self.static_pixmap = None
            return
        painter.setRenderHint(QPainter.Antialiasing)

        center = QPointF(self.width() // 2, self.height() // 2)
        self.radius = min(self.width(), self.height()) // 2 - 60
        
        # Tham số cho hiệu ứng isometric (góc nhìn 45 độ)
        self.cylinder_height = self.radius * 0.2   # Chiều cao của khối trụ
        self.ellipse_height = self.radius * 0.7    # Tăng chiều cao ellipse cho mặt trên/dưới
        self.isometric_factor = math.sin(math.radians(45))  # Hệ số co cho trục Y (view 45 độ)

        # Vẽ giao diện tĩnh với hiệu ứng isometric
        self._draw_isometric_cylinder(painter, center, self.radius)
        
        # Vẽ các vạch và marks trên mặt trên
        top_center = QPointF(center.x(), center.y() - self.cylinder_height/2)
        self._draw_main_line_isometric(painter, top_center, self.radius, (255, 255, 255), 2)
        
        # Vẽ sector và angle lines
        self._fill_sector_isometric(painter, top_center, self.radius, self.redlines, QColor(0, 0, 0, 150))
        self._draw_angle_lines_isometric(painter, top_center, self.radius, self.redlines)
        if painter.isActive():
            painter.end()

    def paintEvent(self, event: QWidget.event) -> None:
        """Vẽ Widget.

        Args:
            event (QWidget.event): The paint event object.

        Returns:
            None
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Vẽ giao diện tĩnh
        if self.static_pixmap:
            painter.drawPixmap(0, 0, self.static_pixmap)

        # Vẽ giao diện động
        center = QPointF(self.width() / 2, self.height() / 2)
        top_center = QPointF(center.x(), center.y() - self.cylinder_height/2)
        
        inner_circle_color = (0, 255, 0, 50) if self._aim_direction == self._current_direction else (255, 255, 255, 50)
        self._draw_isometric_circle(painter, top_center, self.radius * 0.7, inner=True, fill_color=inner_circle_color)
        
        # Vẽ cột mốc góc cho outer circle (không xoay)
        self._draw_angle_marks_static(painter, top_center, self.radius, (255, 255, 255), 1.5)
        
        # Vẽ cột mốc góc cho inner circle (xoay theo w_direction)  
        self._draw_angle_marks_isometric(painter, top_center, self.radius * 0.7, (255, 255, 255), 1.5)
        
        # Vẽ main line cho inner circle (xoay theo w_direction)
        self._draw_main_line_rotated(painter, top_center, self.radius * 0.7, (255, 255, 255), 2)
        
        # # Vẽ cột mốc đỏ cố định cho inner circle (không xoay)
        # self._draw_red_mark_static(painter, top_center, self.radius * 0.7, 2)
        
        # Vẽ la bàn địa lý trên vòng tròn bên trong
        self._draw_geographic_compass(painter, top_center, self.radius * 0.7)
        
        # Vẽ icon tàu xoay theo current_direction
        icon_path = "ui/resources/Icons/ShipIcon.png"
        self._draw_center_icon(painter, top_center, icon_path, self.radius * 0.7)
        
        # Cả 2 mũi tên đều ở vòng ngoài: current_direction hướng ra ngoài, aim_direction hướng vào trong
        self._draw_pointer_triangle_isometric(painter, top_center, self.radius, self._current_direction, 20, inner_circle=False)
        self._draw_pointer_triangle_isometric(painter, top_center, self.radius, self._aim_direction, 20, inner_circle=True)
        
        # Chuyển đường parabol ra vòng ngoài: từ tâm đến đầu mũi tên current (hướng ra ngoài)
        self._draw_parabola_to_outer_triangle(painter, top_center, self.radius, self._current_direction)
        
        # Vẽ missile animation trên đường parabol vòng ngoài
        self._draw_missile_animation_outer(painter, top_center, self.radius, self._current_direction)
        
    def _draw_parabola_to_inner_triangle(self, painter: QPainter, center: QPointF, radius: float, angle_deg: float) -> None:
        """Vẽ đường parabol từ tâm compass đến mũi tam giác bên trong.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            angle_deg (float): Góc của tam giác bên trong (độ).

        Returns:
            None
        """
        angle_rad = math.radians(-angle_deg + 90)

        # Tính toán vị trí mũi tam giác bên trong với phép chiếu isometric
        x_3d = radius * math.cos(angle_rad)
        y_3d = radius * math.sin(angle_rad)
        
        # Biến đổi isometric (góc nhìn 60 độ)
        ellipse_x = x_3d
        ellipse_y = y_3d * self.isometric_factor
        
        # Điểm đích (mũi tam giác)
        end_x = center.x() + ellipse_x
        end_y = center.y() - ellipse_y
        end_point = QPointF(end_x, end_y)

        # Tạo đường parabol
        path = QtGui.QPainterPath()
        path.moveTo(center)
        
        # Điểm điều khiển cho parabol (tạo độ cong)
        # Điểm điều khiển nằm ở giữa và được nâng lên một chút để tạo hình parabol
        control_x = center.x() + ellipse_x * 0.5
        control_y = center.y() - ellipse_y * 0.5 - 30  # Nâng lên 30 pixel để tạo độ cong
        control_point = QPointF(control_x, control_y)
        
        # Vẽ đường cong quadratic (parabol)
        path.quadTo(control_point, end_point)
        
        # Thiết lập màu đỏ và kiểu đứt đoạn cho đường parabol
        pen = QPen(QColor(255, 0, 0, 200), 2)  # Màu đỏ, độ dày 2
        pen.setStyle(Qt.DashLine)  # Đường đứt đoạn
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

    def _draw_parabola_to_outer_triangle(self, painter: QPainter, center: QPointF, radius: float, angle_deg: float) -> None:
        """Vẽ đường parabol từ tâm compass đến đầu mũi tên current_direction trên vòng ngoài.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            angle_deg (float): Góc của mũi tên current_direction (độ).

        Returns:
            None
        """
        angle_rad = math.radians(-angle_deg + 90)

        # Tính toán vị trí đầu mũi tên current_direction trên viền vòng ngoài (giống p1 trong _draw_pointer_triangle_isometric)
        x_3d = radius * math.cos(angle_rad)
        y_3d = radius * math.sin(angle_rad)
        
        # Biến đổi isometric (góc nhìn 60 độ)
        ellipse_x = x_3d
        ellipse_y = y_3d * self.isometric_factor
        
        # Điểm đích (đầu mũi tên current_direction trên viền vòng ngoài)
        end_x = center.x() + ellipse_x
        end_y = center.y() - ellipse_y
        end_point = QPointF(end_x, end_y)

        # Tạo đường parabol
        path = QtGui.QPainterPath()
        path.moveTo(center)
        
        # Điểm điều khiển cho parabol (tạo độ cong)
        # Điểm điều khiển nằm ở giữa và được nâng lên một chút để tạo hình parabol
        control_x = center.x() + ellipse_x * 0.5
        control_y = center.y() - ellipse_y * 0.5 - 40  # Nâng lên 40 pixel để tạo độ cong lớn hơn cho vòng ngoài
        control_point = QPointF(control_x, control_y)
        
        # Vẽ đường cong quadratic (parabol)
        path.quadTo(control_point, end_point)
        
        # Thiết lập màu xanh dương và kiểu đứt đoạn cho đường parabol (đổi từ đỏ sang xanh)
        pen = QPen(QColor(255, 0, 0, 200), 2)  # Màu xanh dương, độ dày 2
        pen.setStyle(Qt.DashLine)  # Đường đứt đoạn
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawPath(path)

    def _draw_missile_animation(self, painter: QPainter, center: QPointF, radius: float, angle_deg: float) -> None:
        """Vẽ missile animation chuyển động theo đường parabol.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            angle_deg (float): Góc của tam giác bên trong (độ).

        Returns:
            None
        """
        angle_rad = math.radians(-angle_deg + 90)

        # Tính toán vị trí mũi tam giác bên trong với phép chiếu isometric
        x_3d = radius * math.cos(angle_rad)
        y_3d = radius * math.sin(angle_rad)
        
        # Biến đổi isometric (góc nhìn 60 độ)
        ellipse_x = x_3d
        ellipse_y = y_3d * self.isometric_factor
        
        # Điểm đích (mũi tam giác)
        end_x = center.x() + ellipse_x
        end_y = center.y() - ellipse_y
        end_point = QPointF(end_x, end_y)

        # Điểm điều khiển cho parabol
        control_x = center.x() + ellipse_x * 0.5
        control_y = center.y() - ellipse_y * 0.5 - 30
        control_point = QPointF(control_x, control_y)
        
        # Tính toán vị trí hiện tại của missile trên đường parabol
        t = self.missile_position
        
        # Sử dụng công thức Bézier quadratic để tính vị trí
        missile_x = (1 - t) * (1 - t) * center.x() + 2 * (1 - t) * t * control_point.x() + t * t * end_point.x()
        missile_y = (1 - t) * (1 - t) * center.y() + 2 * (1 - t) * t * control_point.y() + t * t * end_point.y()
        missile_pos = QPointF(missile_x, missile_y)
        
        # Tính toán góc xoay của missile dựa trên hướng chuyển động
        # Sử dụng phương pháp tính vector hướng dựa trên hai điểm liên tiếp
        if t < 0.95:  # Tránh division by zero khi gần cuối đường
            # Tính vị trí điểm tiếp theo (nhỏ hơn để có hướng chính xác)
            t_next = t + 0.05
            if t_next > 1.0:
                t_next = 1.0
            
            # Vị trí điểm tiếp theo
            next_x = (1 - t_next) * (1 - t_next) * center.x() + 2 * (1 - t_next) * t_next * control_point.x() + t_next * t_next * end_point.x()
            next_y = (1 - t_next) * (1 - t_next) * center.y() + 2 * (1 - t_next) * t_next * control_point.y() + t_next * t_next * end_point.y()
            
            # Tính vector hướng từ vị trí hiện tại đến vị trí tiếp theo
            dx = next_x - missile_x
            dy = next_y - missile_y
            
            # Tính góc của missile - thêm 90 độ vì missile SVG đầu hướng lên trên
            missile_angle = math.atan2(dy, dx) + math.pi/2
        else:
            # Ở cuối đường parabol, missile hướng về phía target
            dx = end_point.x() - missile_x
            dy = end_point.y() - missile_y
            missile_angle = math.atan2(dy, dx) + math.pi/2
        
        # Vẽ missile
        missile_path = "ui/resources/Icons/missile.svg"
        self._draw_missile_icon(painter, missile_pos, missile_path, missile_angle)

    def _draw_missile_animation_outer(self, painter: QPainter, center: QPointF, radius: float, angle_deg: float) -> None:
        """Vẽ missile animation chuyển động theo đường parabol đến đầu mũi tên current_direction.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            angle_deg (float): Góc của mũi tên current_direction (độ).

        Returns:
            None
        """
        angle_rad = math.radians(-angle_deg + 90)

        # Tính toán vị trí đầu mũi tên current_direction trên viền vòng ngoài (giống với _draw_parabola_to_outer_triangle)
        x_3d = radius * math.cos(angle_rad)
        y_3d = radius * math.sin(angle_rad)
        
        # Biến đổi isometric (góc nhìn 60 độ)
        ellipse_x = x_3d
        ellipse_y = y_3d * self.isometric_factor
        
        # Điểm đích (đầu mũi tên current_direction trên viền vòng ngoài)
        end_x = center.x() + ellipse_x
        end_y = center.y() - ellipse_y
        end_point = QPointF(end_x, end_y)

        # Điểm điều khiển cho parabol (tương ứng với _draw_parabola_to_outer_triangle)
        control_x = center.x() + ellipse_x * 0.5
        control_y = center.y() - ellipse_y * 0.5 - 40  # Nâng lên 40 pixel cho vòng ngoài
        control_point = QPointF(control_x, control_y)
        
        # Tính toán vị trí hiện tại của missile trên đường parabol
        t = self.missile_position
        
        # Sử dụng công thức Bézier quadratic để tính vị trí
        missile_x = (1 - t) * (1 - t) * center.x() + 2 * (1 - t) * t * control_point.x() + t * t * end_point.x()
        missile_y = (1 - t) * (1 - t) * center.y() + 2 * (1 - t) * t * control_point.y() + t * t * end_point.y()
        missile_pos = QPointF(missile_x, missile_y)
        
        # Tính toán góc xoay của missile dựa trên hướng chuyển động
        # Sử dụng phương pháp tính vector hướng dựa trên hai điểm liên tiếp
        if t < 0.95:  # Tránh division by zero khi gần cuối đường
            # Tính vị trí điểm tiếp theo (nhỏ hơn để có hướng chính xác)
            t_next = t + 0.05
            if t_next > 1.0:
                t_next = 1.0
            
            # Vị trí điểm tiếp theo
            next_x = (1 - t_next) * (1 - t_next) * center.x() + 2 * (1 - t_next) * t_next * control_point.x() + t_next * t_next * end_point.x()
            next_y = (1 - t_next) * (1 - t_next) * center.y() + 2 * (1 - t_next) * t_next * control_point.y() + t_next * t_next * end_point.y()
            
            # Tính vector hướng từ vị trí hiện tại đến vị trí tiếp theo
            dx = next_x - missile_x
            dy = next_y - missile_y
            
            # Tính góc của missile - thêm 90 độ vì missile SVG đầu hướng lên trên
            missile_angle = math.atan2(dy, dx) + math.pi/2
        else:
            # Ở cuối đường parabol, missile hướng về phía đầu mũi tên current_direction
            dx = end_point.x() - missile_x
            dy = end_point.y() - missile_y
            missile_angle = math.atan2(dy, dx) + math.pi/2
        
        # Vẽ missile
        missile_path = "ui/resources/Icons/missile.svg"
        self._draw_missile_icon(painter, missile_pos, missile_path, missile_angle)

    def _draw_missile_icon(self, painter: QPainter, position: QPointF, icon_path: str, rotation_angle: float) -> None:
        """Vẽ icon missile tại vị trí và góc xoay nhất định.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            position (QPointF): Vị trí để vẽ missile.
            icon_path (str): Đường dẫn đến file SVG của missile.
            rotation_angle (float): Góc xoay của missile (radian).

        Returns:
            None
        """
        # Load missile icon (sử dụng PNG thay vì SVG để đơn giản hóa)
        missile_png_path = "ui/resources/Icons/missile.svg"
        pixmap = QPixmap(missile_png_path)
        if pixmap.isNull():
            print(f"Error: Unable to load missile icon from {missile_png_path}")
            return

        # Kích thước missile (phóng to x1.2)
        missile_size = 24
        pixmap = pixmap.scaled(missile_size, missile_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Tạo một pixmap màu đen từ pixmap gốc
        black_pixmap = QPixmap(pixmap.size())
        black_pixmap.fill(Qt.transparent)
        
        black_painter = QPainter(black_pixmap)
        black_painter.setRenderHint(QPainter.Antialiasing)
        
        # Vẽ hình dạng gốc để giữ alpha channel
        black_painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        black_painter.drawPixmap(0, 0, pixmap)
        
        # Đổi màu thành đen bằng cách vẽ đè lên với màu đen và CompositionMode_SourceAtop
        black_painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        black_painter.fillRect(black_pixmap.rect(), Qt.black)
        
        black_painter.end()

        # Tạo transform để xoay missile theo hướng chuyển động
        transform = QtGui.QTransform()
        transform.translate(position.x(), position.y())
        transform.rotate(math.degrees(rotation_angle))
        transform.translate(-missile_size/2, -missile_size/2)

        painter.save()
        painter.setTransform(transform, True)
        painter.drawPixmap(0, 0, black_pixmap)
        painter.restore()

    def _draw_circle(self, painter: QPainter, center: QPointF, radius:float, color: tuple, thickness: int, fill_color: tuple) -> None:
        """Vẽ hình tròn với tô màu bên trong.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của hình tròn.
            radius (float): Bán kính của hình tròn.
            color (tuple): Màu của đường viền. (R, G, B).
            thickness (int): Độ dày của đường viền.
            fill_color (tuple): Màu tô bên trong hình tròn. (R, G, B, A).

        Returns:
            None
        """
        painter.setPen(QPen(QColor(*color), thickness))
        painter.setBrush(QColor(*fill_color))
        painter.drawEllipse(center, radius, radius)

    def _draw_grid_background(self, painter: QPainter) -> None:
        """Vẽ lưới background với đường kẻ ngang và dọc màu xám trắng mỏng."""
        painter.setPen(QPen(QColor(220, 220, 220, 80), 0.5))  # Màu xám trắng mỏng, trong suốt
        
        # Khoảng cách giữa các đường kẻ
        grid_spacing = 20
        
        # Vẽ các đường kẻ dọc
        for x in range(0, self.width(), grid_spacing):
            painter.drawLine(x, 0, x, self.height())
        
        # Vẽ các đường kẻ ngang
        for y in range(0, self.height(), grid_spacing):
            painter.drawLine(0, y, self.width(), y)

    def _draw_isometric_cylinder(self, painter: QPainter, center: QPointF, radius: float) -> None:
        # Tính toán vị trí tâm ellipse trên và dưới trước khi vẽ các vạch
        ellipse_height_60 = 2 * radius * self.isometric_factor
        top_center_y = center.y() - self.cylinder_height/2
        bottom_center_y = center.y() + self.cylinder_height/2

        # Vẽ các vạch nhỏ (mỗi 15 độ, trừ bội số của 45) ở nửa dưới từ viền ellipse trên xuống viền ellipse dưới
        painter.setPen(QPen(QColor(255, 255, 255), 1.5))
        for angle in range(180, 361, 15):
            if angle % 45 == 0:
                continue
            angle_rad = math.radians(angle)
            x_top = center.x() + radius * math.cos(angle_rad)
            y_top = top_center_y - (radius * math.sin(angle_rad)) * self.isometric_factor
            x_bot = center.x() + radius * math.cos(angle_rad)
            y_bot = bottom_center_y - (radius * math.sin(angle_rad)) * self.isometric_factor
            painter.drawLine(QPointF(x_top, y_top), QPointF(x_bot, y_bot))

        # Vẽ các đường đỏ (angle lines) ở nửa dưới nếu có trong danh sách góc
        painter.setPen(QPen(Qt.red, 2))
        # Sử dụng self.redlines thay vì khai báo cố định
        for angle in self.redlines:
            if angle < 180 or angle > 360:
                continue
            angle_rad = math.radians(angle)
            x_top = center.x() + radius * math.cos(angle_rad)
            y_top = top_center_y - (radius * math.sin(angle_rad)) * self.isometric_factor
            x_bot = center.x() + radius * math.cos(angle_rad)
            y_bot = bottom_center_y - (radius * math.sin(angle_rad)) * self.isometric_factor
            painter.drawLine(QPointF(x_top, y_top), QPointF(x_bot, y_bot))

        # Vẽ các đường dọc từ viền ellipse trên xuống viền ellipse dưới, chỉ ở nửa dưới (góc 180° đến 360°)
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        for i in range(4, 8):  # 4*45=180, 7*45=315
            angle_deg = i * 45
            angle_rad = math.radians(angle_deg)
            # Điểm trên ellipse trên (viền ngoài)
            x_top = center.x() + radius * math.cos(angle_rad)
            y_top = top_center_y - (radius * math.sin(angle_rad)) * self.isometric_factor
            # Điểm trên ellipse dưới (viền ngoài)
            x_bot = center.x() + radius * math.cos(angle_rad)
            y_bot = bottom_center_y - (radius * math.sin(angle_rad)) * self.isometric_factor
            painter.drawLine(QPointF(x_top, y_top), QPointF(x_bot, y_bot))
        """Vẽ khối trụ isometric với hiệu ứng 3D với góc nhìn 60 độ và thêm đổ bóng."""
        # Khởi tạo side_gradient ngay từ đầu để tránh lỗi
        side_gradient = QtGui.QLinearGradient(center.x() - radius, center.y(), 
                                              center.x() + radius, center.y())
        side_gradient.setColorAt(0, QColor(50, 50, 150))     # Dark blue on the left
        side_gradient.setColorAt(0.5, QColor(100, 150, 200)) # Medium blue in the center
        side_gradient.setColorAt(1, QColor(150, 200, 255))   # Light blue on the right

        # Vẽ đổ bóng trước
        shadow_gradient = QtGui.QRadialGradient(center.x(), center.y() + self.cylinder_height, radius * 1.2)
        shadow_gradient.setColorAt(0, QColor(0, 0, 0, 100))  # Màu đen nhạt ở giữa
        shadow_gradient.setColorAt(1, QColor(0, 0, 0, 0))    # Trong suốt ở viền

        painter.setBrush(QtGui.QBrush(shadow_gradient))
        painter.setPen(Qt.NoPen)
        shadow_rect = QRectF(center.x() - radius * 1.2, center.y() + self.cylinder_height/2,
                             2 * radius * 1.2, radius * 0.6)
        painter.drawEllipse(shadow_rect)

        # Vẽ mặt dưới (ellipse tối hơn) với góc nhìn 60 độ TRƯỚC mặt bên
        bottom_gradient = QtGui.QRadialGradient(center.x(), center.y() + self.cylinder_height/2, radius)
        bottom_gradient.setColorAt(0, QColor(128, 128, 128, 180))  # 50% gray at the center
        bottom_gradient.setColorAt(1, QColor(100, 100, 100, 200))  # Slightly darker gray at the edges

        painter.setBrush(QtGui.QBrush(bottom_gradient))
        painter.setPen(QPen(QColor(100, 100, 100), 2))

        # Ellipse dưới với góc nhìn 60 độ - chỉ vẽ nửa dưới
        ellipse_height_60 = 2 * radius * self.isometric_factor
        ellipse_bottom_rect = QRectF(center.x() - radius, center.y() + self.cylinder_height/2 - ellipse_height_60/2,
                          2 * radius, ellipse_height_60)
        path = QtGui.QPainterPath()
        # Điểm đầu bên trái (góc 180 độ)
        left = QPointF(center.x() - radius, center.y() + self.cylinder_height/2)
        # Vẽ cung nửa dưới ellipse (từ 180 đến 360 độ)
        path.moveTo(left)
        path.arcTo(ellipse_bottom_rect, 180, 180)
        # Không vẽ đường kẻ ngang đóng path
        painter.setBrush(Qt.NoBrush)
        painter.setPen(QPen(QColor(160, 160, 160), 4))  # Viền ellipse dưới dày hơn (4 thay vì 2)
        painter.drawPath(path)

        # Vẽ viền mỏng bên trái và phải cho khối trụ nối sát mép ellipse trên và dưới
        border_color = QColor(160, 160, 160)
        border_thickness = 4  # Viền khối trụ dày hơn (4 thay vì 2)
        painter.setPen(QPen(border_color, border_thickness))
        # Tính toán vị trí tâm của ellipse trên và dưới
        top_center_y = center.y() - self.cylinder_height/2
        bottom_center_y = center.y() + self.cylinder_height/2
        
        # Bên trái: nối từ điểm tiếp xúc của ellipse trên đến ellipse dưới
        x_left = center.x() - radius
        painter.drawLine(QPointF(x_left, top_center_y), QPointF(x_left, bottom_center_y))
        # Bên phải: nối từ điểm tiếp xúc của ellipse trên đến ellipse dưới
        x_right = center.x() + radius
        painter.drawLine(QPointF(x_right, top_center_y), QPointF(x_right, bottom_center_y))

        # Vẽ mặt trên (ellipse sáng hơn) với góc nhìn 60 độ - có alpha để hơi trong suốt
        top_gradient = QtGui.QRadialGradient(center.x(), center.y() - self.cylinder_height/2, radius)
        top_gradient.setColorAt(0, QColor(180, 180, 180, 255))    # Xám sáng ở giữa, alpha 255
        top_gradient.setColorAt(0.7, QColor(140, 140, 140, 255))  # Xám trung bình, alpha 255
        top_gradient.setColorAt(1, QColor(100, 100, 100, 255))    # Xám tối ở viền, alpha 255

        painter.setBrush(QtGui.QBrush(top_gradient))
        painter.setPen(QPen(QColor(160, 160, 160), 4))  # Viền mặt trên dày hơn (4 thay vì 2)

        # Ellipse trên với góc nhìn 60 độ
        ellipse_top_rect = QRectF(center.x() - radius, center.y() - self.cylinder_height/2 - ellipse_height_60/2,
                          2 * radius, ellipse_height_60)
        painter.drawEllipse(ellipse_top_rect)

    def _draw_isometric_circle(self, painter: QPainter, center: QPointF, radius: float, inner: bool = False, fill_color: tuple = None) -> None:
        """Vẽ ellipse trên mặt trên của khối trụ isometric với góc nhìn 60 độ, với phần tròn giữa trong suốt 50%."""
        if fill_color is None:
            if inner:
                fill_color = (255, 255, 255, 30)  # 50% trong suốt
            else:
                fill_color = (255, 255, 255, 255)
        
        # Vẽ mặt trên với hiệu ứng gradient màu xám
        top_gradient = QtGui.QRadialGradient(center.x(), center.y() - self.ellipse_height/4, radius)
        if inner:
            # Vòng tròn bên trong có màu xám nhạt hơn
            top_gradient.setColorAt(0, QColor(200, 200, 200, 120))
            top_gradient.setColorAt(0.7, QColor(170, 170, 170, 100))
            top_gradient.setColorAt(1, QColor(140, 140, 140, 80))
        else:
            # Vòng tròn bên ngoài có màu xám đậm hơn
            top_gradient.setColorAt(0, QColor(180, 180, 180, 150))
            top_gradient.setColorAt(0.7, QColor(150, 150, 150, 120))
            top_gradient.setColorAt(1, QColor(120, 120, 120, 100))
        
        painter.setBrush(QtGui.QBrush(top_gradient))
        painter.setPen(QPen(QColor(255, 255, 255), 4 if not inner else 1))  # Viền vòng ngoài dày hơn (4 thay vì 2)
        
        # Vẽ ellipse với góc nhìn 60 độ (co trục Y theo tỷ lệ sin(60°))
        ellipse_height_60 = 2 * radius * self.isometric_factor
        painter.drawEllipse(QRectF(center.x() - radius, center.y() - ellipse_height_60/2,
                          2 * radius, ellipse_height_60))

    def _draw_main_line(self, painter: QPainter, center: QPointF, radius: float, color: tuple, thickness: int) -> None:
        """Vẽ các vạch dài trên đồng hồ để chỉ hướng. Mỗi vạch dài cách nhau 45 độ.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của vòng tròn.
            radius (float): Bán kính của vòng tròn.
            color (tuple): Màu của vạch. (R, G, B).
            thickness (int): Độ dày của vạch.

        Returns:
            None
        """
        painter.setPen(QPen(QColor(*color), thickness))

        for i in range(8):  # 8 hướng chính (E, SE, S, SW, W, NW, N, NE)
            angle_deg = i * 45
            angle_rad = math.radians(angle_deg)

            # Tính toán vị trí của tick mark
            start_x = center.x() + radius * 0.9 * math.cos(angle_rad)
            start_y = center.y() - radius * 0.9 * math.sin(angle_rad)
            end_x = center.x() + radius * math.cos(angle_rad)
            end_y = center.y() - radius * math.sin(angle_rad)

            # Vẽ tick mark
            painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))

    def _draw_main_line_isometric(self, painter: QPainter, center: QPointF, radius: float, color: tuple, thickness: int) -> None:
        """Vẽ các vạch dài trên đồng hồ isometric với góc nhìn 60 độ. Mỗi vạch dài cách nhau 45 độ.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            color (tuple): Màu của vạch. (R, G, B).
            thickness (int): Độ dày của vạch.

        Returns:
            None
        """
        for i in range(8):  # 8 hướng chính (E, SE, S, SW, W, NW, N, NE)
            angle_deg = i * 45
            angle_rad = math.radians(angle_deg)

            # Tính toán vị trí với phép chiếu isometric 60 độ
            x_3d = radius * 0.9 * math.cos(angle_rad)
            y_3d = radius * 0.9 * math.sin(angle_rad)
            
            # Biến đổi isometric (góc nhìn 60 độ)
            start_x = center.x() + x_3d
            start_y = center.y() - y_3d * self.isometric_factor
            
            x2_3d = radius * math.cos(angle_rad)
            y2_3d = radius * math.sin(angle_rad)
            
            end_x = center.x() + x2_3d
            end_y = center.y() - y2_3d * self.isometric_factor

            # Kiểm tra nếu là góc 0 độ thì vẽ màu đỏ
            if angle_deg == 90:
                painter.setPen(QPen(Qt.red, thickness + 1))  # Màu đỏ và dày hơn
            else:
                painter.setPen(QPen(QColor(*color), thickness))

            # Vẽ tick mark
            painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))

    def _draw_angle_marks(self, painter: QPainter, center: QPointF, radius: float, color: tuple, thickness: int) -> None:
        """Vẽ các vạch trên đông hồ để chỉ góc. Mỗi vạch cách nhau 15 độ.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của vòng tròn.
            radius (float): Bán kính của vòng tròn.
            color (tuple): Màu của vạch. (R, G, B).
            thickness (int): Độ dày của vạch.

        Returns:
            None
        """
        painter.setPen(QPen(QColor(*color), thickness))

        for angle in range(0, 360, 15):  # Tick marks mỗi 15 độ
            angle_rad = math.radians(angle)

            # Tính toán vị trí của tick mark
            start_x = center.x() + radius * 0.94 * math.cos(angle_rad)
            start_y = center.y() - radius * 0.94 * math.sin(angle_rad)
            end_x = center.x() + radius * math.cos(angle_rad)
            end_y = center.y() - radius * math.sin(angle_rad)

            # Vẽ tick mark
            if angle % 45 != 0:  # Vẽ chữ số cho các góc chính
                painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))

    def _draw_main_line_rotated(self, painter: QPainter, center: QPointF, radius: float, color: tuple, thickness: int) -> None:
        """Vẽ các vạch dài xoay theo w_direction.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            color (tuple): Màu của vạch. (R, G, B).
            thickness (int): Độ dày của vạch.

        Returns:
            None
        """
        for i in range(8):  # 8 hướng chính (E, SE, S, SW, W, NW, N, NE)
            angle_deg = i * 45
            # Áp dụng w_direction để xoay
            rotated_angle = (angle_deg + self._w_direction) % 360
            angle_rad = math.radians(rotated_angle)

            # Tính toán vị trí với phép chiếu isometric 60 độ
            x_3d = radius * 0.9 * math.cos(angle_rad)
            y_3d = radius * 0.9 * math.sin(angle_rad)
            
            # Biến đổi isometric (góc nhìn 60 độ)
            start_x = center.x() + x_3d
            start_y = center.y() - y_3d * self.isometric_factor
            
            x2_3d = radius * math.cos(angle_rad)
            y2_3d = radius * math.sin(angle_rad)
            
            end_x = center.x() + x2_3d
            end_y = center.y() - y2_3d * self.isometric_factor

            # Vẽ vạch dài
            painter.setPen(QPen(QColor(*color), thickness))
            painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))

    def _draw_angle_marks_isometric(self, painter: QPainter, center: QPointF, radius: float, color: tuple, thickness: int) -> None:
        """Vẽ các vạch trên đồng hồ isometric với góc nhìn 60 độ để chỉ góc. Mỗi vạch cách nhau 15 độ.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            color (tuple): Màu của vạch. (R, G, B).
            thickness (int): Độ dày của vạch.

        Returns:
            None
        """
        for angle in range(0, 360, 15):  # Tick marks mỗi 15 độ
            # Áp dụng w_direction để xoay toàn bộ hệ tọa độ
            rotated_angle = (angle + self._w_direction) % 360
            angle_rad = math.radians(rotated_angle)

            # Tính toán vị trí với phép chiếu isometric 60 độ
            x_3d = radius * 0.94 * math.cos(angle_rad)
            y_3d = radius * 0.94 * math.sin(angle_rad)
            
            # Biến đổi isometric (góc nhìn 60 độ)
            start_x = center.x() + x_3d
            start_y = center.y() - y_3d * self.isometric_factor
            
            x2_3d = radius * math.cos(angle_rad)
            y2_3d = radius * math.sin(angle_rad)
            
            end_x = center.x() + x2_3d
            end_y = center.y() - y2_3d * self.isometric_factor

            # Vẽ tick mark
            if angle % 45 != 0:  # Vẽ cho các góc không phải bội số của 45
                painter.setPen(QPen(QColor(*color), thickness))
                painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))

    def _draw_angle_marks_static(self, painter: QPainter, center: QPointF, radius: float, color: tuple, thickness: int) -> None:
        """Vẽ các vạch cố định trên đồng hồ isometric (không xoay theo w_direction).

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            color (tuple): Màu của vạch. (R, G, B).
            thickness (int): Độ dày của vạch.

        Returns:
            None
        """
        for angle in range(0, 360, 15):  # Tick marks mỗi 15 độ
            angle_rad = math.radians(angle)

            # Tính toán vị trí với phép chiếu isometric 60 độ
            x_3d = radius * 0.94 * math.cos(angle_rad)
            y_3d = radius * 0.94 * math.sin(angle_rad)
            
            # Biến đổi isometric (góc nhìn 60 độ)
            start_x = center.x() + x_3d
            start_y = center.y() - y_3d * self.isometric_factor
            
            x2_3d = radius * math.cos(angle_rad)
            y2_3d = radius * math.sin(angle_rad)
            
            end_x = center.x() + x2_3d
            end_y = center.y() - y2_3d * self.isometric_factor

            # Vẽ tick mark
            if angle % 45 != 0:  # Vẽ cho các góc không phải bội số của 45
                painter.setPen(QPen(QColor(*color), thickness))
                painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))

    def _draw_red_mark_static(self, painter: QPainter, center: QPointF, radius: float, thickness: int) -> None:
        """Vẽ cột mốc đỏ cố định ở góc 135 độ (không xoay theo w_direction).

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            thickness (int): Độ dày của vạch.

        Returns:
            None
        """
        angle = 90  # Góc cố định 135 độ
        angle_rad = math.radians(angle)

        # Tính toán vị trí với phép chiếu isometric
        x_3d = radius * 0.94 * math.cos(angle_rad)
        y_3d = radius * 0.94 * math.sin(angle_rad)
        
        # Biến đổi isometric
        start_x = center.x() + x_3d
        start_y = center.y() - y_3d * self.isometric_factor
        
        x2_3d = radius * math.cos(angle_rad)
        y2_3d = radius * math.sin(angle_rad)
        
        end_x = center.x() + x2_3d
        end_y = center.y() - y2_3d * self.isometric_factor

        # Vẽ cột mốc đỏ
        painter.setPen(QPen(Qt.red, thickness + 1))  # Màu đỏ và dày hơn
        painter.drawLine(QPointF(start_x, start_y), QPointF(end_x, end_y))

    def _draw_center_icon(self, painter: QPainter, center: QPointF, icon_path: str, inner_radius: float) -> None:
        """Vẽ icon ở giữa vòng tròn, nghiêng về phía trước để tạo góc nhìn 45 độ từ phía sau."""
        pixmap = QPixmap(icon_path)
        if pixmap.isNull():
            print(f"Error: Unable to load icon from {icon_path}")
            return

        # Tính toán kích thước icon dựa trên bán kính vòng tròn nhỏ
        icon_size = int(inner_radius)  # Giảm kích thước icon nhỏ hơn
        pixmap = pixmap.scaled(icon_size, icon_size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # Tạo transform để nghiêng icon về phía trước
        transform = QtGui.QTransform()  # Xoay 90 độ về bên trái 
        transformed_pixmap = pixmap.transformed(transform, Qt.SmoothTransformation)

        # Tính toán tọa độ góc trên bên trái để căn giữa icon
        top_left_x = center.x() - transformed_pixmap.width() / 2 
        top_left_y = center.y() - transformed_pixmap.height() / 2 

        # Vẽ icon
        painter.drawPixmap(int(top_left_x), int(top_left_y), transformed_pixmap)

    def _draw_pointer_triangle(self, painter: QPainter, center: QPointF, radius: float, angle_deg: float, size: float, inner_circle: bool = True) -> None:
        """Vẽ con trỏ tam giác chỉ góc hiện tại trên vòng tròn.

        Args:
            painter (QPainter): Đối tượng QPainter cho việ vẽ.
            center (QPointF): Tọa độ trung tâm của vòng tròn.
            radius (float): Bán kính của vòng tròn.
            angle_deg (float): Góc hiện tại (độ).
            size (float): Kích thước của tam giác.
            inner_circle (bool): Nếu True, vẽ tam giác bên trong vòng tròn. Nếu False, vẽ bên ngoài.

        Returns:
            None
        """
        angle_rad = math.radians(-angle_deg + 90)

        # Đỉnh đầu tiên nằm trên đường tròn
        x1 = center.x() + radius * math.cos(angle_rad)
        y1 = center.y() - radius * math.sin(angle_rad)
        p1 = QPointF(x1, y1)

        # Hai đỉnh còn lại để tạo tam giác đều
        if inner_circle:
            # Tam giác bên trong hướng từ tâm ra ngoài (ngược lại)
            angle1 = angle_rad + math.radians(150)  # Đảo hướng tam giác
            angle2 = angle_rad - math.radians(150)
        else:
            # Tam giác bên ngoài hướng ra ngoài bình thường
            angle1 = angle_rad + math.radians(30)
            angle2 = angle_rad - math.radians(30)

        x2 = x1 + size * math.cos(angle1)
        y2 = y1 - size * math.sin(angle1)
        x3 = x1 + size * math.cos(angle2)
        y3 = y1 - size * math.sin(angle2)

        p2 = QPointF(x2, y2)
        p3 = QPointF(x3, y3)

        # Vẽ tam giác với màu sắc tùy theo inner_circle
        if inner_circle:
            painter.setPen(Qt.NoPen)  # Bỏ viền
            painter.setBrush(Qt.black)  # Tam giác bên trong màu đen
        else:
            painter.setPen(Qt.NoPen)  # Bỏ viền
            painter.setBrush(Qt.white)  # Tam giác bên ngoài màu trắng
        
        painter.drawPolygon([p1, p2, p3])

        # Tính toán tọa độ của chữ
        if inner_circle:
            text_distance = radius * 0.7
        else:
            # Vị trí text quay thêm 180 độ (từ phía đối diện sang cùng phía với đỉnh)
            text_distance = radius * 0.9
            
        x4 = center.x() + text_distance * math.cos(angle_rad)
        y4 = center.y() - text_distance * math.sin(angle_rad)
        p4 = QPointF(x4, y4)

        text_rect = QRectF(p4.x() - 20, p4.y() - 10, 40, 20)
        
        # Thiết lập font
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        # Vẽ nền xám cho text
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(80, 80, 80, 180))  # Nền xám trong suốt
        painter.drawRoundedRect(text_rect, 3, 3)
        
        # Vẽ text màu trắng
        painter.setPen(QPen(Qt.white, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawText(text_rect, Qt.AlignCenter, f"{angle_deg:.0f}°")

    def _draw_pointer_triangle_isometric(self, painter: QPainter, center: QPointF, radius: float, angle_deg: float, size: float, inner_circle: bool = True) -> None:
        """Vẽ con trỏ tam giác chỉ góc hiện tại trên ellipse isometric với góc nhìn 60 độ.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của ellipse.
            radius (float): Bán kính của ellipse.
            angle_deg (float): Góc hiện tại (độ).
            size (float): Kích thước của tam giác.
            inner_circle (bool): Nếu True, mũi tên hướng vào trong. Nếu False, mũi tên hướng ra ngoài.

        Returns:
            None
        """

        angle_rad = math.radians(-angle_deg + 90)

        # Tính toán vị trí với phép chiếu isometric 60 độ - đầu mũi tên luôn nằm trên viền vòng ngoài
        x_3d = radius * math.cos(angle_rad)
        y_3d = radius * math.sin(angle_rad)
        
        # Biến đổi isometric (góc nhìn 60 độ)
        ellipse_x = x_3d
        ellipse_y = y_3d * self.isometric_factor
        
        # Đỉnh đầu tiên nằm trên ellipse ngoài (đầu mũi tên)
        x1 = center.x() + ellipse_x
        y1 = center.y() - ellipse_y
        p1 = QPointF(x1, y1)

        # Hai đỉnh còn lại để tạo tam giác đều
        if inner_circle:
            # Mũi tên aim_direction: hướng vào trong (từ viền vào tâm)
            angle1 = angle_rad + math.radians(30)   # Hướng vào trong
            angle2 = angle_rad - math.radians(30)
        else:
            # Mũi tên current_direction: hướng ra ngoài (từ tâm ra viền)
            angle1 = angle_rad + math.radians(150)  # Hướng ra ngoài
            angle2 = angle_rad - math.radians(150)

        x2 = x1 + size * math.cos(angle1)
        y2 = y1 - size * math.sin(angle1)
        x3 = x1 + size * math.cos(angle2)
        y3 = y1 - size * math.sin(angle2)

        p2 = QPointF(x2, y2)
        p3 = QPointF(x3, y3)

        # Vẽ tam giác với màu sắc tùy theo inner_circle và góc độ
        angle_diff = abs(self._current_direction - self._aim_direction)
        # Xử lý trường hợp góc vượt qua 360/0 độ
        if angle_diff > 180:
            angle_diff = 360 - angle_diff
            
        if inner_circle:
            painter.setPen(Qt.NoPen)  # Bỏ viền
            # Mũi tên aim_direction: trắng thông thường, đỏ khi góc gần bằng nhau
            if angle_diff <= 1.0:  # Lệch ≤ 1 độ
                painter.setBrush(Qt.red)  # Chuyển đỏ khi góc gần bằng nhau
            else:
                painter.setBrush(Qt.white)  # Mũi tên aim_direction màu trắng (đã đổi từ đỏ)
        else:
            painter.setPen(Qt.NoPen)  # Bỏ viền
            painter.setBrush(Qt.black)  # Mũi tên current_direction màu đen (đã đổi từ trắng)
        
        painter.drawPolygon([p1, p2, p3])

        # Tính toán tọa độ của chữ - dịch ra phía ngoài tam giác
        if inner_circle:
            # Mũi tên aim_direction (hướng vào trong): text dịch ra ngoài theo hướng từ tâm ra
            text_distance = radius * 1.3  # Tăng khoảng cách ra ngoài hơn
        else:
            # Mũi tên current_direction (hướng ra ngoài): text dịch ra ngoài theo hướng tam giác
            text_distance = radius * 0.7  # Tăng khoảng cách ra ngoài nhiều hơn
            
        text_angle = angle_rad
        text_x_3d = text_distance * math.cos(text_angle)
        text_y_3d = text_distance * math.sin(text_angle)
        text_x = center.x() + text_x_3d
        text_y = center.y() - text_y_3d * self.isometric_factor
        p4 = QPointF(text_x, text_y)

        text_rect = QRectF(p4.x() - 20, p4.y() - 10, 40, 20)
        
        # Thiết lập font
        font = painter.font()
        font.setPointSize(9)
        font.setBold(True)
        painter.setFont(font)
        
        # Vẽ nền xám cho text
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(80, 80, 80, 180))  # Nền xám trong suốt
        painter.drawRoundedRect(text_rect, 3, 3)
        
        # Vẽ text màu trắng
        painter.setPen(QPen(Qt.white, 1))
        painter.setBrush(Qt.NoBrush)
        painter.drawText(text_rect, Qt.AlignCenter, f"{angle_deg:.0f}°")

    def _fill_sector(self, painter: QPainter, center: QPointF, radius: float, start_angle: float, end_angle: float, color: QColor) -> None:
        """Fill một phần hình tròn từ start_angle đến end_angle.

        Args:
            painter (QPainter): Đối tượng QPainter để vẽ.
            center (QPointF): Tâm của hình tròn.
            radius (float): Bán kính của hình tròn.
            start_angle (float): Góc bắt đầu (độ).
            end_angle (float): Góc kết thúc (độ).
            color (QColor): Màu để fill.

        Returns:
            None
        """
        path = QtGui.QPainterPath()
        path.moveTo(center)
        path.arcTo(center.x() - radius, center.y() - radius, 2 * radius, 2 * radius, start_angle, end_angle - start_angle)
        path.closeSubpath()

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

    def _fill_sector_isometric(self, painter: QPainter, center: QPointF, radius: float, angles: list, color: QColor) -> None:
        """Fill một phần ellipse từ start_angle đến end_angle cho isometric view với góc nhìn 60 độ.

        Args:
            painter (QPainter): Đối tượng QPainter để vẽ.
            center (QPointF): Tâm của ellipse.
            radius (float): Bán kính của ellipse.
            start_angle (float): Góc bắt đầu (độ).
            end_angle (float): Góc kết thúc (độ).
            color (QColor): Màu để fill.

        Returns:
            None
        """
        path = QtGui.QPainterPath()
        path.moveTo(center)
        start_angle = angles[0] + 90
        end_angle = 450 - angles[1]
        # Tạo arc cho ellipse với góc nhìn 60 độ
        ellipse_height_60 = 2 * radius * self.isometric_factor
        ellipse_rect = QRectF(center.x() - radius, center.y() - ellipse_height_60/2, 
                             2 * radius, ellipse_height_60)
        path.arcTo(ellipse_rect, start_angle, end_angle - start_angle)
        path.closeSubpath()

        painter.setBrush(color)
        painter.setPen(Qt.NoPen)
        painter.drawPath(path)

    def _draw_angle_lines(self, painter: QPainter, center: QPointF, radius: float, angles: list) -> None:
        """Vẽ các đường từ tâm ở các góc chỉ định.

        Args:
            painter (QPainter): Đối tượng QPainter để vẽ.
            center (QPointF): Tâm của hình tròn.
            radius (float): Bán kính của hình tròn.
            angles (list): Danh sách các góc (độ) để vẽ đường.

        Returns:
            None
        """
        painter.setPen(QPen(Qt.red, 2))
        for angle in angles:
            angle_rad = math.radians(angle)
            end_x = center.x() + radius * math.cos(angle_rad)
            end_y = center.y() - radius * math.sin(angle_rad)
            painter.drawLine(center, QPointF(end_x, end_y))

    def _draw_angle_lines_isometric(self, painter: QPainter, center: QPointF, radius: float, angles: list) -> None:
        """Vẽ các đường từ tâm ở các góc chỉ định cho isometric view với góc nhìn 60 độ.

        Args:
            painter (QPainter): Đối tượng QPainter để vẽ.
            center (QPointF): Tâm của ellipse.
            radius (float): Bán kính của ellipse.
            angles (list): Danh sách các góc (độ) để vẽ đường.

        Returns:
            None
        """
        painter.setPen(QPen(Qt.red, 2))
        change_angle = [angles[0] + 90, 450 - angles[1]]
        for angle in change_angle:
            angle_rad = math.radians(angle)
            # Tính toán vị trí với phép chiếu isometric 60 độ
            x_3d = radius * math.cos(angle_rad)
            y_3d = radius * math.sin(angle_rad)
            
            # Biến đổi isometric (góc nhìn 60 độ)
            end_x = center.x() + x_3d
            end_y = center.y() - y_3d * self.isometric_factor
            painter.drawLine(center, QPointF(end_x, end_y))

    def _draw_geographic_compass(self, painter: QPainter, center: QPointF, radius: float) -> None:
        """Vẽ la bàn địa lý với các chữ cái N, E, S, W xoay theo w_direction.

        Args:
            painter (QPainter): Đối tượng QPainter cho việc vẽ.
            center (QPointF): Tọa độ trung tâm của vòng tròn.
            radius (float): Bán kính của vòng tròn.

        Returns:
            None
        """
        # Thiết lập font cho chữ cái
        font = painter.font()
        font.setPointSize(14)
        font.setBold(True)
        painter.setFont(font)
        
        # Các hướng địa lý: chỉ giữ N
        directions = [
            ("N", 0, Qt.red),      # Bắc - màu đỏ
            ("S", 180, Qt.blue)    # Nam - màu xanh dương
        ]
        
        for direction_text, base_angle, color in directions:
            # Tính góc thực tế sau khi xoay theo w_direction
            # w_direction = 0 nghĩa là tàu hướng Bắc
            # w_direction = 90 nghĩa là tàu hướng Đông
            actual_angle = (base_angle - self._w_direction) % 360
            angle_rad = math.radians(-actual_angle + 90)  # Chuyển đổi tọa độ màn hình
            
            # Tính vị trí text với phép chiếu isometric
            text_distance = radius * 0.85  # Đặt text gần viền vòng tròn
            x_3d = text_distance * math.cos(angle_rad)
            y_3d = text_distance * math.sin(angle_rad)
            
            # Biến đổi isometric
            text_x = center.x() + x_3d
            text_y = center.y() - y_3d * self.isometric_factor
            
            # Vẽ text
            text_rect = QRectF(text_x - 15, text_y - 10, 30, 20)
            
            # Vẽ viền trắng cho chữ S màu xanh để dễ nhìn hơn
            if direction_text == "S":
                # Vẽ viền trắng bằng cách vẽ text nhiều lần với offset nhỏ
                painter.setPen(QPen(Qt.white, 4))  # Viền trắng dày
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx != 0 or dy != 0:  # Không vẽ ở vị trí trung tâm
                            offset_rect = QRectF(text_x - 15 + dx, text_y - 10 + dy, 30, 20)
                            painter.drawText(offset_rect, Qt.AlignCenter, direction_text)
            
            # Vẽ text chính
            painter.setPen(QPen(color, 2))
            painter.drawText(text_rect, Qt.AlignCenter, direction_text)
