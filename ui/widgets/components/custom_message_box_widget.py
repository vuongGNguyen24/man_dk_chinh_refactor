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
        if self.parent():
            self.setGeometry(self.parent().rect())  # phủ full parent
        
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
        
        if self.parent():
            self.setGeometry(self.parent().rect())  # phủ full parent
        self.show()
        self.raise_()

