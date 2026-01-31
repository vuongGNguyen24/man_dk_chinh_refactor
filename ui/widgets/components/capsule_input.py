from PyQt5.QtWidgets import (QHBoxLayout, QLabel,
                             QLineEdit, QWidget, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator

class CapsuleInput(QWidget):
    """Widget hình viên thuốc với 3 phần: label - input - đơn vị."""

    def __init__(self, label_text, default_value="0", unit_text="", parent=None):
        super().__init__(parent)
        self.label_text = label_text
        self.unit_text = unit_text

        # Tạo layout chính
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Container cho viên thuốc
        capsule = QWidget()
        capsule.setFixedHeight(40)
        capsule_layout = QHBoxLayout(capsule)
        capsule_layout.setContentsMargins(0, 0, 0, 0)
        capsule_layout.setSpacing(0)

        # Label bên trái
        self.label = QLabel(label_text)
        self.label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.label.setFixedHeight(40)
        self.label.setStyleSheet("""
            QLabel {
                background-color: #525252;
                color: #F1F5F9;
                font-size: 14px;
                font-family: 'Tahoma', Arial, sans-serif;
                padding-left: 20px;
                border-top-left-radius: 25px;
                border-bottom-left-radius: 25px;
            }
        """)
        self.label.setMinimumWidth(180)
        capsule_layout.addWidget(self.label)

        # Đường phân cách giữa label và input
        separator1 = QFrame()
        separator1.setFrameShape(QFrame.VLine)
        separator1.setFixedWidth(1)
        separator1.setStyleSheet("background-color: #F1F5F9;")
        capsule_layout.addWidget(separator1)

        # Input ở giữa
        self.input_field = QLineEdit(default_value)
        self.input_field.setValidator(QDoubleValidator())
        self.input_field.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Căn phải
        self.input_field.setFixedHeight(40)
        self.input_field.setStyleSheet("""
            QLineEdit {
                background-color: #525252;
                color: #F1F5F9;
                border: none;
                font-size: 15px;
                font-weight: bold;
                font-family: 'Tahoma', Arial, sans-serif;
                padding-right: 10px;
            }
            QLineEdit:focus {
                background-color: #626262;
            }
            QLineEdit:disabled {
                background-color: #3a3a3a;
                color: #808080;
            }
        """)
        self.input_field.setFixedWidth(100)  # Tăng lên 100px
        capsule_layout.addWidget(self.input_field)

        # Đường phân cách giữa input và đơn vị
        separator2 = QFrame()
        separator2.setFrameShape(QFrame.VLine)
        separator2.setFixedWidth(1)
        separator2.setStyleSheet("background-color: #F1F5F9;")
        capsule_layout.addWidget(separator2)

        # Đơn vị bên phải
        self.unit_label = QLabel(unit_text)
        self.unit_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)  # Căn phải
        self.unit_label.setFixedHeight(40)
        self.unit_label.setStyleSheet("""
            QLabel {
                background-color: #525252;
                color: #F1F5F9;
                font-size: 14px;
                font-family: 'Tahoma', Arial, sans-serif;
                padding-right: 15px;
                border-top-right-radius: 25px;
                border-bottom-right-radius: 25px;
            }
        """)
        self.unit_label.setFixedWidth(100)  # Tăng lên 100px
        capsule_layout.addWidget(self.unit_label)

        layout.addWidget(capsule)

    def text(self):
        """Lấy text từ input field."""
        return self.input_field.text()

    def setText(self, text):
        """Set text cho input field."""
        self.input_field.setText(text)

    def setEnabled(self, enabled):
        """Enable/disable input field và đổi màu toàn bộ capsule."""
        self.input_field.setEnabled(enabled)
        
        # Đổi màu label bên trái
        if enabled:
            self.label.setStyleSheet("""
                QLabel {
                    background-color: #525252;
                    color: #F1F5F9;
                    font-size: 14px;
                    font-family: 'Tahoma', Arial, sans-serif;
                    padding-left: 20px;
                    border-top-left-radius: 25px;
                    border-bottom-left-radius: 25px;
                }
            """)
            self.unit_label.setStyleSheet("""
                QLabel {
                    background-color: #525252;
                    color: #F1F5F9;
                    font-size: 14px;
                    font-family: 'Tahoma', Arial, sans-serif;
                    padding-right: 15px;
                    border-top-right-radius: 25px;
                    border-bottom-right-radius: 25px;
                }
            """)
        else:
            self.label.setStyleSheet("""
                QLabel {
                    background-color: #3a3a3a;
                    color: #808080;
                    font-size: 14px;
                    font-family: 'Tahoma', Arial, sans-serif;
                    padding-left: 20px;
                    border-top-left-radius: 25px;
                    border-bottom-left-radius: 25px;
                }
            """)
            self.unit_label.setStyleSheet("""
                QLabel {
                    background-color: #3a3a3a;
                    color: #808080;
                    font-size: 14px;
                    font-family: 'Tahoma', Arial, sans-serif;
                    padding-right: 15px;
                    border-top-right-radius: 25px;
                    border-bottom-right-radius: 25px;
                }
            """)
        
        super().setEnabled(enabled)

    @property
    def textChanged(self):
        """Signal khi text thay đổi."""
        return self.input_field.textChanged