from PyQt5.QtWidgets import QMessageBox, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGraphicsOpacityEffect
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QColor

class ConfirmationWidget(QWidget):
    """Widget overlay để xác nhận hành động - hiển thị trên tab thay vì popup."""
    
    # Signals
    confirmed = pyqtSignal()  # Khi nhấn OK
    cancelled = pyqtSignal()  # Khi nhấn Cancel
    
    def __init__(self, title="Xác nhận", message="Bạn có chắc chắn?", parent=None):
        super().__init__(parent)
        self.title = title
        self.message = message
        
        # Làm cho widget này hiển thị trên tất cả widget khác
        self.setWindowFlags(Qt.Widget)
        self.setAttribute(Qt.WA_TranslucentBackground, True)  # Nền trong suốt hoàn toàn
        
        self.setupUi()
        
    def setupUi(self):
        # Layout chính - chỉ chứa dialog container
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Container cho dialog
        self.dialog_container = QWidget()
        self.dialog_container.setFixedWidth(400)
        self.dialog_container.setObjectName("confirmDialog")
        
        layout = QVBoxLayout(self.dialog_container)
        layout.setContentsMargins(30, 25, 30, 25)
        layout.setSpacing(20)
        
        # Title
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #ffffff;
                background-color: transparent;
                border: none;
            }
        """)
        
        # Message
        self.message_label = QLabel(self.message)
        self.message_label.setAlignment(Qt.AlignCenter)
        self.message_label.setWordWrap(True)
        self.message_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #cccccc;
                background-color: transparent;
                border: none;
                padding: 10px;
            }
        """)
        
        # Buttons layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(20)
        
        self.cancel_button = QPushButton("Hủy")
        self.cancel_button.setMinimumHeight(45)
        self.cancel_button.setMinimumWidth(120)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
            QPushButton:pressed {
                background-color: #991B1B;
            }
        """)
        self.cancel_button.clicked.connect(self._on_cancel)
        
        self.ok_button = QPushButton("Xác nhận")
        self.ok_button.setMinimumHeight(45)
        self.ok_button.setMinimumWidth(120)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.ok_button.clicked.connect(self._on_confirm)
        
        button_layout.addStretch()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.ok_button)
        button_layout.addStretch()
        
        # Add to layout
        layout.addWidget(self.title_label)
        layout.addWidget(self.message_label)
        layout.addSpacing(10)
        layout.addLayout(button_layout)
        
        # Style cho dialog container
        self.dialog_container.setStyleSheet("""
            QWidget#confirmDialog {
                background-color: #1a1a1a;
                border: 2px solid #0078d4;
                border-radius: 15px;
            }
        """)
        
        # Center dialog trong main layout
        main_layout.addStretch()
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        h_layout.addWidget(self.dialog_container)
        h_layout.addStretch()
        main_layout.addLayout(h_layout)
        main_layout.addStretch()
        
    def paintEvent(self, event):
        """Vẽ nền trong suốt."""
        # Không vẽ gì - để nền trong suốt
        pass
        
    def set_message(self, title, message):
        """Cập nhật title và message."""
        self.title = title
        self.message = message
        self.title_label.setText(title)
        self.message_label.setText(message)
            
    def _on_confirm(self):
        """Xử lý khi nhấn OK."""
        self.hide()
        self.confirmed.emit()
        
    def _on_cancel(self):
        """Xử lý khi nhấn Cancel."""
        self.hide()
        self.cancelled.emit()
        
    def show_confirmation(self, title, message):
        """Hiển thị dialog xác nhận với title và message mới."""
        self.set_message(title, message)
        self.show()
        self.raise_()


class CustomMessageBox:
    """Custom message box với style thống nhất."""
    
    STYLE_SHEET = """
        QMessageBox {
            background-color: #1E293B;
            color: #F1F5F9;
            border-radius: 16px;
            border: 1.5px solid rgba(0,0,0,0.2);
            font-family: 'Tahoma', Arial, sans-serif;
            font-size: 16px;
            min-width: 340px;
        }
        QMessageBox QLabel {
            font-size: 16px;
            color: #F1F5F9;
            background: transparent;
        }
        QMessageBox QPushButton {
            background-color: #10B981;
            color: #F1F5F9;
            padding: 7px 24px;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
            margin: 0 8px;
            min-width: 100px;
        }
        QMessageBox QPushButton:hover {
            background-color: #059669;
        }
        QMessageBox QPushButton:pressed {
            background-color: #3B82F6;
        }
        /* Nút Cancel (No) */
        QMessageBox QPushButton[role="reject"],
        QMessageBox QPushButton:flat {
            background-color: #DC2626;
            color: #F1F5F9;
        }
        /* Nút OK (Yes) */
        QMessageBox QPushButton[role="accept"] {
            background-color: #10B981;
            color: #F1F5F9;
        }
    """

    @staticmethod
    def _center_on_screen(msg):
        """Đặt popup ở giữa màn hình."""
        if msg.parent():
            # Nếu có parent, đặt ở giữa parent
            parent_geometry = msg.parent().geometry()
            msg.move(
                parent_geometry.center().x() - msg.width() // 2,
                parent_geometry.center().y() - msg.height() // 2
            )
        else:
            # Nếu không có parent, đặt ở giữa màn hình
            screen_geometry = msg.screen().availableGeometry()
            msg.move(
                screen_geometry.center().x() - msg.width() // 2,
                screen_geometry.center().y() - msg.height() // 2
            )

    @staticmethod
    def warning(title, message, parent=None):
        """Hiển thị message box cảnh báo (không icon)."""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        # Không setIcon
        msg.setStyleSheet(CustomMessageBox.STYLE_SHEET)
        # Đặt ở giữa màn hình
        msg.adjustSize()
        CustomMessageBox._center_on_screen(msg)
        return msg.exec_()

    @staticmethod
    def question(title, message, parent=None):
        """Hiển thị message box xác nhận (không icon, OK xanh, Cancel đỏ)."""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        # Không setIcon
        yes = msg.addButton("OK", QMessageBox.YesRole)
        no = msg.addButton("Cancel", QMessageBox.NoRole)
        msg.setDefaultButton(yes)
        msg.setStyleSheet(CustomMessageBox.STYLE_SHEET)
        # Đặt màu cho từng nút bằng setStyleSheet riêng
        yes.setStyleSheet("background-color: #10B981; color: #F1F5F9; border-radius: 8px; font-weight: bold; font-size: 15px; min-width: 100px; margin: 0 8px;")
        no.setStyleSheet("background-color: #DC2626; color: #F1F5F9; border-radius: 8px; font-weight: bold; font-size: 15px; min-width: 100px; margin: 0 8px;")
        # Đặt ở giữa màn hình
        msg.adjustSize()
        CustomMessageBox._center_on_screen(msg)
        result = msg.exec_()
        if msg.clickedButton() == yes:
            return QMessageBox.Yes
        else:
            return QMessageBox.No

    @staticmethod
    def information(title, message, parent=None):
        """Hiển thị message box thông báo (không icon, không setIcon khi phóng thành công, nút OK xanh)."""
        msg = QMessageBox(parent)
        msg.setWindowTitle(title)
        msg.setText(message)
        # Không setIcon
        ok = msg.addButton("OK", QMessageBox.AcceptRole)
        msg.setDefaultButton(ok)
        msg.setStyleSheet(CustomMessageBox.STYLE_SHEET)
        ok.setStyleSheet("background-color: #10B981; color: #F1F5F9; border-radius: 8px; font-weight: bold; font-size: 15px; min-width: 100px; margin: 0 8px;")
        # Đặt ở giữa màn hình
        msg.adjustSize()
        CustomMessageBox._center_on_screen(msg)
        return msg.exec_()