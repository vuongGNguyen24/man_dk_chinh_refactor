from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPainter, QPen, QBrush, QColor


class ThresholdEditorDialog(QDialog):
    """Custom threshold editor dialog with dark styling matching the specifications."""

    threshold_updated = pyqtSignal(str, float, float)  # parameter_name, min_value, max_value

    def __init__(self, parameter_name, current_min=50.0, current_max=50.0, parent=None):
        super().__init__(parent)
        self.parameter_name = parameter_name
        self.current_min = current_min
        self.current_max = current_max

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setFixedSize(400, 200)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.init_ui()

    def init_ui(self):
        """Initialize the custom UI elements."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # Header section with parameter name and V icon
        header_layout = QHBoxLayout()

        # Parameter name label
        self.param_label = QLabel(self.parameter_name)
        self.param_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Tahoma', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                background: transparent;
            }
        """)
        header_layout.addWidget(self.param_label)

        # Spacer to push V icon to the right
        header_layout.addStretch()

        # V icon (circular border with V inside)
        self.v_icon_label = QLabel("V")
        self.v_icon_label.setFixedSize(30, 30)
        self.v_icon_label.setAlignment(Qt.AlignCenter)
        self.v_icon_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Tahoma', Arial, sans-serif;
                font-size: 14px;
                font-weight: bold;
                border: 2px solid white;
                border-radius: 15px;
                background: transparent;
            }
        """)
        header_layout.addWidget(self.v_icon_label)

        main_layout.addLayout(header_layout)

        # Minimum value section
        min_layout = QHBoxLayout()
        min_label = QLabel("Minimum value threshold")
        min_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Tahoma', Arial, sans-serif;
                font-size: 12px;
                background: transparent;
            }
        """)

        self.min_input = QLineEdit(str(self.current_min))
        self.min_input.setFixedSize(80, 30)
        self.min_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #3B82F6;
                border-radius: 4px;
                padding: 5px;
                color: white;
                background-color: #3b3b3b;
                font-family: 'Tahoma', Arial, sans-serif;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #60A5FA;
            }
        """)

        min_layout.addWidget(min_label)
        min_layout.addStretch()
        min_layout.addWidget(self.min_input)

        main_layout.addLayout(min_layout)

        # Maximum value section
        max_layout = QHBoxLayout()
        max_label = QLabel("Maximum value threshold")
        max_label.setStyleSheet("""
            QLabel {
                color: white;
                font-family: 'Tahoma', Arial, sans-serif;
                font-size: 12px;
                background: transparent;
            }
        """)

        self.max_input = QLineEdit(str(self.current_max))
        self.max_input.setFixedSize(80, 30)
        self.max_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #3B82F6;
                border-radius: 4px;
                padding: 5px;
                color: white;
                background-color: #3b3b3b;
                font-family: 'Tahoma', Arial, sans-serif;
                font-size: 12px;
            }
            QLineEdit:focus {
                border-color: #60A5FA;
            }
        """)

        max_layout.addWidget(max_label)
        max_layout.addStretch()
        max_layout.addWidget(self.max_input)

        main_layout.addLayout(max_layout)

        # Add stretch to push everything up
        main_layout.addStretch()

        # Button section (hidden initially, can be added later)
        button_layout = QHBoxLayout()

        self.ok_button = QPushButton("OK")
        self.ok_button.setFixedSize(60, 25)
        self.ok_button.setStyleSheet("""
            QPushButton {
                background-color: #10B981;
                color: white;
                border: none;
                border-radius: 4px;
                font-family: 'Tahoma', Arial, sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
            QPushButton:pressed {
                background-color: #047857;
            }
        """)
        self.ok_button.clicked.connect(self.accept_changes)

        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.setFixedSize(60, 25)
        self.cancel_button.setStyleSheet("""
            QPushButton {
                background-color: #DC2626;
                color: white;
                border: none;
                border-radius: 4px;
                font-family: 'Tahoma', Arial, sans-serif;
                font-size: 11px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #B91C1C;
            }
            QPushButton:pressed {
                background-color: #991B1B;
            }
        """)
        self.cancel_button.clicked.connect(self.reject)

        button_layout.addStretch()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)

        main_layout.addLayout(button_layout)

        # Connect Enter key to accept
        self.min_input.returnPressed.connect(self.accept_changes)
        self.max_input.returnPressed.connect(self.accept_changes)

    def paintEvent(self, event):
        """Custom paint event for rounded rectangle background and connecting line."""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw rounded rectangle background
        rect = self.rect()
        painter.setBrush(QBrush(QColor(59, 59, 59)))  # #3b3b3b
        painter.setPen(QPen(QColor(0, 0, 0, 0)))  # No border
        painter.drawRoundedRect(rect, 8, 8)

        # Draw close button (X) in top-right corner
        close_rect_size = 20
        close_x = rect.width() - close_rect_size - 10
        close_y = 10

        # Draw close button background (optional)
        painter.setPen(QPen(QColor(255, 255, 255), 1))
        painter.setBrush(QBrush(QColor(0, 0, 0, 0)))  # Transparent
        painter.drawRect(close_x, close_y, close_rect_size, close_rect_size)

        # Draw X
        painter.setPen(QPen(QColor(255, 255, 255), 2))
        margin = 6
        painter.drawLine(close_x + margin, close_y + margin,
                        close_x + close_rect_size - margin, close_y + close_rect_size - margin)
        painter.drawLine(close_x + close_rect_size - margin, close_y + margin,
                        close_x + margin, close_y + close_rect_size - margin)

        # Store close button rect for mouse events
        self.close_button_rect = (close_x, close_y, close_rect_size, close_rect_size)

        # Draw connecting line between parameter name and V icon
        if hasattr(self, 'param_label') and hasattr(self, 'v_icon_label'):
            param_right = self.param_label.geometry().right()
            v_left = self.v_icon_label.geometry().left()
            y_center = self.param_label.geometry().center().y()

            painter.setPen(QPen(QColor(59, 130, 246), 2))  # Light blue line #3B82F6
            painter.drawLine(param_right + 10, y_center, v_left - 10, y_center)

    def mousePressEvent(self, event):
        """Handle mouse press events for close button."""
        if hasattr(self, 'close_button_rect'):
            x, y, w, h = self.close_button_rect
            if (x <= event.x() <= x + w and y <= event.y() <= y + h):
                self.reject()
                return
        super().mousePressEvent(event)

    def accept_changes(self):
        """Accept the changes and emit signal."""
        try:
            min_val = float(self.min_input.text())
            max_val = float(self.max_input.text())

            if min_val >= max_val:
                # Show error (could use CustomMessageBox here)
                return

            self.threshold_updated.emit(self.parameter_name, min_val, max_val)
            self.accept()
        except ValueError:
            # Invalid input, ignore
            pass

    def keyPressEvent(self, event):
        """Handle key press events."""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)


# Example usage and integration function
def show_threshold_editor(parameter_name, current_min=50.0, current_max=50.0, parent=None):
    """
    Show threshold editor dialog for a parameter.

    Args:
        parameter_name (str): Name of the parameter to edit
        current_min (float): Current minimum threshold value
        current_max (float): Current maximum threshold value
        parent: Parent widget

    Returns:
        tuple: (min_value, max_value) if accepted, None if cancelled
    """
    dialog = ThresholdEditorDialog(parameter_name, current_min, current_max, parent)

    def on_threshold_updated(param_name, min_val, max_val):
        # Store the result values for later retrieval
        dialog.result_values = (min_val, max_val)

    dialog.threshold_updated.connect(on_threshold_updated)
    dialog.result_values = None

    if dialog.exec_() == QDialog.Accepted:
        return getattr(dialog, 'result_values', None)
    return None