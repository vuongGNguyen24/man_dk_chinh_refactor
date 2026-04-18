from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Set, Dict

from ..components.isometric_buttons import IsometricButton, IsometricVisualState, IsometricRoundButton
from ui.styles.isometric_button.praser import IsometricTheme
import ui.helpers.qss as qss

NUMBER_LIST = [[ 2,10,14,17,11, 3],
               [ 6,16, 8, 5,15, 7],
               [ 4,12,18,13, 9, 1]]

class BulletIsometricButton(IsometricRoundButton):
    def __init__(self, index: int, parent=None):
        # state tạm, sẽ được apply từ ngoài
        super().__init__(state=None, parent=parent)
        self.index = index
        self.setFont(QFont("Tahoma", 18, QFont.Bold))
        self.setText(str(index))
        self.setFixedSize(70, 86)  # 80 + depth
        
        
class BulletWidget(QWidget):

    launcher_clicked = pyqtSignal(str, int)
    # side, index
    
    def __init__(self, parent=None):
        super().__init__(parent)

        self._buttons: Dict[str, Dict[int, BulletIsometricButton]] = {
            "left": {},
            "right": {},
        }
        self.isometric_theme = IsometricTheme("ui/styles/isometric_button/theme.yaml")
        self._create_launcher_frame("Giàn trái", 10, 15)
        self._create_launcher_frame("Giàn phải", 630, 15)
        
    def _create_launcher_frame(self, title: str, x: int, y: int):
        frame = QLabel(self)
        frame.setGeometry(x, y, 590, 320)
        frame.setObjectName("launcher-frame")
        qss.set_multiple_property(frame, role="bullet-widget", variant="background")
        title_label = QLabel(title, self)
        title_label.setGeometry(x, y, 590, 34)
        title_label.setAlignment(Qt.AlignCenter)
        qss.set_multiple_property(title_label, role="bullet-widget", variant="title")
        
        launcher_id = 'left' if 'trái' in title else 'right'
        self._create_launcher_buttons(launcher_id, x, y)
        
    def _create_launcher_buttons(self, launcher_id: str, base_x: int, base_y: int):
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
                    lambda _, s=launcher_id, i=index:
                    self.launcher_clicked.emit(s, i)
                )

                self._buttons[launcher_id][index] = btn
    
    def update_launcher(
        self,
        side: str,
        status: List[bool],
        selected: Set[int]
    ):
        """
        status: [True/False] * 18
        selected: set các index được chọn
        colors: dict màu (adapter quyết định)
        """
        DISABLED, ENABLED, EMPTY_AND_SELECTED, SELECTED = 0, 1, 2, 3    
        color_map = {
            DISABLED: self.isometric_theme(f"IsometricButton", 'disabled'),
            ENABLED: self.isometric_theme(f"IsometricButton", 'enabled'),
            SELECTED: self.isometric_theme(f"IsometricButton", 'selected'),
            EMPTY_AND_SELECTED: self.isometric_theme(f"IsometricButton", 'empty_and_selected'),
        }
        
        #recalculate status
        for index in range(1, len(status) + 1):
            status[index - 1] = status[index - 1] | ((index in selected) << 1)
                
        
        for i in range(len(status)):
            #bullet wigdet is 1-indexed based
            btn = self._buttons[side][i + 1]
            btn.setFont(QFont("Tahoma", 18, QFont.Bold))
            
            btn.apply_visual_state(color_map[status[i]])



if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from PyQt5.QtGui import QColor
    from typing import Dict

    app = QApplication(sys.argv)
    qss.load_app_qss(app, ["ui/styles/bullet_widget.qss"])
    widget = BulletWidget(None)
    widget.resize(800, 600)
    # widget.setStyleSheet("background-color: #121212;")

    widget.update_launcher(
        "Giàn trái",
        [True] * 18,
        {1, 2, 3, 4, 5, 6, 7, 8},
    )
    widget.update_launcher(
        "Giàn phải",
        [False] * 18,
        {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18},
    )

    widget.show()
    app.exec_()
