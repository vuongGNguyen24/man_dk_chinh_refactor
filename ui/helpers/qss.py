from typing import List
from PyQt5.QtWidgets import QApplication

def load_app_qss(app: QApplication, paths: List[str]):
    """Load qss files cho Qt application.
    
    
    File sau sẽ override style của các file đã load trước!
    
    Args:
        app (QApplication): application object cần load style
        paths (List[str]): danh sách đường đẫn các file .qss, theo thứ tự load style.
    """
    styles = []
    for path in paths:
        with open(path, "r", encoding="utf-8") as f:
            styles.append(f.read())
    app.setStyleSheet("\n".join(styles))
    

def repolish(widget):
    """Cập nhật style cho qt element sau khi setProperty.
    
    Args:
        widget (QWidget): widget cần update style
    """
    widget.style().unpolish(widget)
    widget.style().polish(widget)
    widget.update()

