from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import pyqtSignal, Qt

class ClickableLabel(QLabel):
    clicked = pyqtSignal(str)

    def __init__(self, node_id: str, parent=None):
        super().__init__(parent)
        self._node_id = node_id
        self.setCursor(Qt.PointingHandCursor)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._node_id)
        super().mousePressEvent(event)
    
    @staticmethod
    def from_qlabel(
        parent,
        object_name: str,
        node_id: str
    ):
        old = parent.findChild(QLabel, object_name)
        if old is None:
            raise RuntimeError(f"Label '{object_name}' not found")

        real_parent = old.parentWidget()
        geometry = old.geometry()

        new = ClickableLabel(node_id=node_id, parent=real_parent)
        new.setGeometry(geometry)
        new.setObjectName(object_name)

        # copy semantic content
        new.setFont(old.font())
        new.setText(old.text())
        new.setAlignment(old.alignment())
        new.setWordWrap(old.wordWrap())

        if old.pixmap():
            new.setPixmap(old.pixmap())

        # copy dynamic properties (quan trọng cho QSS)
        for name in old.dynamicPropertyNames():
            new.setProperty(name.data().decode(), old.property(name.data().decode()))

        old.deleteLater()
        new.show()
        return new
