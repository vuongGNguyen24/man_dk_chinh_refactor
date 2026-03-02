from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

class LogTab(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._apply_roles()

    def _setup_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.title_label = QtWidgets.QLabel("Lịch sử sự kiện")
        self.title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title_label)

        self.log_browser = QtWidgets.QTextBrowser()
        layout.addWidget(self.log_browser)

        self.clear_btn = QtWidgets.QPushButton("Xóa lịch sử")
        self.clear_btn.clicked.connect(self.clear)
        layout.addWidget(self.clear_btn)

    def _apply_roles(self):
        # container
        self.setProperty("role", "dialog")
        self.setProperty("variant", "confirm")  # dùng container dialog style

        self.title_label.setProperty("role", "log-title")

        self.log_browser.setProperty("role", "log-view")
        self.clear_btn.setProperty("role", "action")
        self.clear_btn.setProperty("state", "cancel")

    # -------- View API --------

    def append_html(self, html: str):
        self.log_browser.append(html)
        self.log_browser.verticalScrollBar().setValue(
            self.log_browser.verticalScrollBar().maximum()
        )

    def clear(self):
        self.log_browser.clear()


if __name__ == "__main__":
    
    import sys
    from PyQt5.QtWidgets import QApplication
    from ui.helpers.qss import load_app_qss
    from adapters.outbound.ui.log_tab import LogTabAdapter
    from application.dto import LogEvent
    from datetime import datetime
    import time
    start_time = time.time() 
    app = QApplication(sys.argv)
    #set qss file
    main_tab = LogTab(None)
    load_app_qss(app, ["ui/styles/dialog.qss", "ui/styles/log_tab.qss"])
    log_adapter = LogTabAdapter(main_tab)
    print(main_tab.styleSheet())
    log_adapter.append(LogEvent(datetime.now(), "INFO", "Hello World!"))
    log_adapter.append(LogEvent(datetime.now(), "SUCCESS", "Hello World!"))
    
    main_tab.show()
    end_time = time.time()
    sys.exit(app.exec_())