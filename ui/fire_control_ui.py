# -*- coding: utf-8 -*-
import yaml
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from ui.views.main_control_tab import MainTab
from ui.views.system_info_tab import InfoTab
from ui.views.log_tab import LogTab
from ui.widgets.features.compass_widget import resource_path


class FireControl(QtCore.QObject):
    TAB_MAIN = 0
    TAB_INFO = 1
    TAB_LOG = 2

    def __init__(self):
        super().__init__()
        with open(resource_path("config.yaml"), "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)

    def setupUi(self, MainWindow):
        self._setup_window(MainWindow)
        self._setup_tabbar(MainWindow)
        self._setup_stack(MainWindow)
        self._wire_events()

        MainWindow.setCentralWidget(self.stack)
        self._switch_tab(self.TAB_MAIN, self.tab_main)

    # --------------------------------------------------
    # Window
    # --------------------------------------------------
    def _setup_window(self, MainWindow):
        cfg = self.config["MainWindow"]

        MainWindow.setObjectName("FireControl")
        MainWindow.resize(cfg["width"], cfg["height"])

        from PyQt5.QtGui import QIcon, QPixmap
        pix = QPixmap(resource_path("ui/resources/Icons/Vietnam.png"))
        if not pix.isNull():
            MainWindow.setWindowIcon(QIcon(pix))

        MainWindow.setStyleSheet(self._load_qss())

    def _load_qss(self):
        qss = ""
        for name in ("base.qss", "tabbar.qss", "pages.qss"):
            with open(resource_path(f"ui/styles/{name}"), encoding="utf-8") as f:
                qss += f.read()
        return qss

    # --------------------------------------------------
    # Tab bar
    # --------------------------------------------------
    def _setup_tabbar(self, parent):
        self.tab_bar = QtWidgets.QWidget(parent)
        self.tab_bar.setObjectName("TopTabBar")
        self.tab_bar.setGeometry(0, 0, parent.width(), 34)

        self.tab_main = self._make_tab("Điều khiển", 8)
        self.tab_info = self._make_tab("Thông tin", 236)
        self.tab_log = self._make_tab("Lịch sử", 464)

        # error indicator
        self.error_indicator = QtWidgets.QLabel(self.tab_log)
        self.error_indicator.setObjectName("ErrorDot")
        self.error_indicator.hide()

    def _make_tab(self, text, x):
        btn = QtWidgets.QPushButton(text, self.tab_bar)
        btn.setObjectName("TopTabButton")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setGeometry(x, 6, 220, 28)
        btn.setProperty("active", False)
        return btn

    # --------------------------------------------------
    # Stack
    # --------------------------------------------------
    def _setup_stack(self, parent):
        tab_h = 34
        self.stack = QtWidgets.QStackedWidget(parent)
        self.stack.setObjectName("MainStack")
        self.stack.setGeometry(
            0, tab_h,
            parent.width(),
            parent.height() - tab_h
        )

        self.stack.addWidget(MainTab(self.config, self.stack))
        self.stack.addWidget(InfoTab(self.config, self.stack))
        self.stack.addWidget(LogTab(self.config, self.stack))

    # --------------------------------------------------
    # Events
    # --------------------------------------------------
    def _wire_events(self):
        self.tab_main.clicked.connect(
            lambda: self._switch_tab(self.TAB_MAIN, self.tab_main)
        )
        self.tab_info.clicked.connect(
            lambda: self._switch_tab(self.TAB_INFO, self.tab_info)
        )
        self.tab_log.clicked.connect(
            lambda: self._switch_tab(self.TAB_LOG, self.tab_log)
        )

    def _switch_tab(self, index, active_btn):
        self.stack.setCurrentIndex(index)

        for btn in (self.tab_main, self.tab_info,
                    self.tab_log, self.tab_settings):
            btn.setProperty("active", btn is active_btn)
            btn.style().unpolish(btn)
            btn.style().polish(btn)

        if index == self.TAB_LOG:
            self.error_indicator.hide()

    # --------------------------------------------------
    # API cho LogTab
    # --------------------------------------------------
    def show_error_indicator(self):
        if self.stack.currentIndex() != self.TAB_LOG:
            self.error_indicator.show()
