from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Set, Dict

from ..components.isometric_buttons import IsometricButton, IsometricVisualState, IsometricRoundButton


NUMBER_LIST = [[ 2,10,14,17,11, 3],
               [ 6,16, 8, 5,15, 7],
               [ 4,12,18,13, 9, 1]]

class BulletIsometricButton(IsometricRoundButton):
    def __init__(self, index: int, parent=None):
        # state tạm, sẽ được apply từ ngoài
        super().__init__(state=None, parent=parent)
        self.index = index
        self.setText(str(index))
        self.setFont(QFont("Tahoma", 18, QFont.Bold))
        self.setFixedSize(70, 86)  # 80 + depth

    def update_visual(
        self,
        ready: bool,
        selected: bool,
        colors: Dict[str, QColor],
        depth: float = 6.0,
    ):
        """
        colors = {
            "ready": QColor,
            "selected": QColor,
            "disabled": QColor,
            "border": QColor,
            "text": QColor,
        }
        """
        if not ready:
            top = colors["disabled"]
        elif selected:
            top = colors["selected"]
        else:
            top = colors["ready"]

        state = IsometricVisualState(
            top_color=top,
            border_color=colors["border"],
            text_color=colors["text"],
            depth=depth,
            enabled=ready,
        )

        self.apply_visual_state(state)
        
        
class BulletWidget(QWidget):

    launcher_clicked = pyqtSignal(str, int)
    # side, index
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self._buttons = {
            "Giàn trái": {},
            "Giàn phải": {},
        }

        self._create_launcher_frame("Giàn trái", 10, 15)
        self._create_launcher_frame("Giàn phải", 630, 15)
        
    def _create_launcher_frame(self, title: str, x: int, y: int):
        frame = QLabel(self)
        frame.setGeometry(x, y, 590, 320)
        frame.setObjectName("launcher-frame")

        title_label = QLabel(title, self)
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #F1F5F9;")
        title_label.setGeometry(x, y, 590, 34)
        title_label.setAlignment(Qt.AlignCenter)
        self._create_launcher_buttons(title, x, y)
        
    def _create_launcher_buttons(self, side: str, base_x: int, base_y: int):
        button_size = 70
        cols, rows = 6, 3

        h_space = (590 - cols * button_size) // (cols + 1)
        v_space = (320 - 30 - rows * button_size) // (rows + 1)

        for r, row in enumerate(NUMBER_LIST):
            for c, index in enumerate(row):
                x = base_x + h_space + c * (button_size + h_space)
                y = base_y + 30 + v_space + r * (button_size + v_space)

                btn = BulletIsometricButton(index, self)
                btn.setGeometry(x, y, button_size, 86)

                btn.clicked.connect(
                    lambda _, s=side, i=index:
                    self.launcher_clicked.emit(s, i)
                )

                self._buttons[side][index] = btn
                
    
    def update_launcher(
        self,
        side: str,
        status: List[bool],
        selected: Set[int],
        colors: Dict[str, QColor],
    ):
        """
        status: [True/False] * 18
        selected: set các index được chọn
        colors: dict màu (adapter quyết định)
        """
        for index, btn in self._buttons[side].items():
            btn.update_visual(
                ready=status[index - 1],
                selected=index in selected,
                colors=colors,
            )



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QColor
    from typing import Dict

    app = QApplication(sys.argv)
    widget = BulletWidget(None)
    widget.resize(800, 600)
    widget.setStyleSheet("background-color: #121212;")

    colors = {
        "ready": QColor(0, 200, 0),
        "selected": QColor(0, 255, 0),
        "disabled": QColor(128, 128, 128),
        "border": QColor(80, 80, 80),
        "text": QColor(255, 255, 255),
    }

    widget.update_launcher(
        "Giàn trái",
        [True] * 18,
        {1, 2, 3, 4, 5, 6, 7, 8},
        colors,
    )
    widget.update_launcher(
        "Giàn phải",
        [False] * 18,
        {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18},
        colors,
    )

    widget.show()
    app.exec_()
