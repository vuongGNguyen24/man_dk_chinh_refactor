from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

class BallisticCalculatorWidget(QWidget):
    accepted = QtCore.pyqtSignal()
    canceled = QtCore.pyqtSignal()
    def __init__(self, ui_path, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WA_StyledBackground, True)
        loadUi(ui_path, self)

        self._bind_roles()
        self._connect_signals()

    def _bind_roles(self):
        self.setProperty("role", "ballistic")
        self.setProperty("variant", "main")

        self.leftPanelTitle.setProperty("role", "section-title")
        self.modeSelectorTitle.setProperty("role", "section-title")
        self.radioButtonsContainer.setProperty("role", "mode-radio")
        
    
    
    
    def _connect_signals(self):
        self.okButton.clicked.connect(self.accepted.emit)
        self.cancelButton.clicked.connect(self.canceled.emit)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = BallisticCalculatorWidget("ui/views//ballistic_calculator/ballistic_calculator.ui")
    widget.show()
    sys.exit(app.exec_())