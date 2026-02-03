
from PyQt5.QtWidgets import QWidget
from PyQt5.uic import loadUi

class BallisticCalculatorWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        loadUi("ui/views/ballistic_calculator.ui", self)

        self._bind_roles()
        self._connect_signals()

    def _bind_roles(self):
        self.setProperty("role", "ballistic")
        self.setProperty("variant", "main")

        self.leftPanelTitle.setProperty("role", "section-title")
        self.modeSelectorTitle.setProperty("role", "section-title")
        self.radioButtonsContainer.setProperty("role", "mode-radio")
        
    
    def _connect_signals(self):
        pass


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = BallisticCalculatorWidget(None)
    widget.show()
    sys.exit(app.exec_())