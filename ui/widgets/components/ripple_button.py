from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox, QColorDialog, QSpinBox, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QGroupBox
from PyQt5.QtCore import Qt, QRectF, QTimer, QPointF, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QRadialGradient
from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QLinearGradient

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
            
if __name__ == "__main__":
    from PyQt5.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    widget = RippleButton("Click me")
    widget.resize(400, 300)
    widget.setStyleSheet("background-color: pink;")
    widget.show()
    sys.exit(app.exec_())
