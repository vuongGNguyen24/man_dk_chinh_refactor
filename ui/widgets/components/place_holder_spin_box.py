from typing import Tuple
from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import Qt


class PlaceholderDoubleSpinBox(QDoubleSpinBox):
    def __init__(self, parent=None, range: Tuple[float, float] = None, decimals: int = 2, step: float = 1):
        super().__init__(parent)
        self._placeholder = ""
        self._is_empty = True

        self.setKeyboardTracking(False)
        self.lineEdit().textChanged.connect(self._on_text_edited)
        self.setDecimals(decimals)
        self.setSingleStep(step)

        if range:
            self.setRange(*range)
        self.setButtonSymbols(QDoubleSpinBox.NoButtons)
    def setPlaceholderText(self, text: str):
        self._placeholder = text
        self._update_placeholder()

    def clear(self):
        self._is_empty = True
        self.lineEdit().clear()
        self._update_placeholder()

    def value(self):
        if self._is_empty:
            return None
        return super().value()

    def _on_text_edited(self, text):
        if text.strip() == "":
            self._is_empty = True
            self._update_placeholder()
        else:
            self._is_empty = False

    def _update_placeholder(self):
        if self._is_empty:
            self.lineEdit().setPlaceholderText(self._placeholder)
        else:
            self.lineEdit().setPlaceholderText("")