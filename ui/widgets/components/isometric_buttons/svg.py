from typing import Union, Tuple

from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QColor
from .pill import IsometricPillButton
from .base import IsometricVisualState
from ....helpers.svg_icon import apply_svg_icon_to_button


class SVGIsometricButton(IsometricPillButton):
    """
    Helper để setup QPushButton với SVG icon có recolor.
    Không render, không load config, không biết domain.
    """
    def __init__(self, state: IsometricVisualState, svg_path: str,
        icon_size: Tuple[int, int] = (48, 48), parent=None):
        super().__init__(state, parent)
        
        #assume svg_color is same type as text_color
        icon_color = self.qcolor_to_hex(state.text_color)
        icon_alpha = state.text_color.alpha()
        
        apply_svg_icon_to_button(self, svg_path, icon_color, QSize(*icon_size), icon_alpha)
        self._apply_basic_style(icon_color, None, 8)
    
    @staticmethod
    def qcolor_to_hex(color: QColor) -> str:
        """
        Convert QColor to '#rrggbb' string.
        
        Alpha channel is ignored.
        """
        if not isinstance(color, QColor):
            raise TypeError("Input must be QColor")

        if not color.isValid():
            raise ValueError("Invalid QColor")

        return color.name(QColor.HexRgb)

    def _apply_basic_style(
        self,
        background: str,
        border_color: Union[str, None],
        border_radius: int,
    ):
        if border_color in (None, "transparent"):
            border = "none"
        else:
            border = f"1px solid {border_color}"

        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {background};
                border: {border};
                border-radius: {border_radius}px;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,0.08);
            }}
            QPushButton:pressed {{
                background-color: rgba(0,0,0,0.25);
            }}
        """)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from .base import IsometricButton, IsometricVisualState
    from PyQt5.QtGui import QColor
    app = QApplication(sys.argv)
    button = SVGIsometricButton(state=IsometricVisualState(QColor(255, 0, 0), QColor(0, 0, 255), QColor(0, 255, 0), 0.5), svg_path=r"C:\Users\Admin\Desktop\projects\wm18\man_dk_chinh_refactor\ui\resources\Icons\calculator.svg")
    button.set_depth(2.5)
    button.pressed = True
    # button = SVGIsometricButton(r"C:\Users\Admin\Desktop\projects\wm18\man_dk_chinh_refactor\ui\resources\Icons\calculator.svg")
    button.show()
    sys.exit(app.exec_())