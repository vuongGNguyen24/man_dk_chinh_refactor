# -*- coding: utf-8 -*-
import yaml
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt

from ui.views import MainTab, InfoTab, LogTab, FiringCircultTab, MainCircultTab
import ui.helpers.qss as qss

class FireControlUI(QtWidgets.QMainWindow):
    TAB_MAIN = 0
    TAB_INFO = 1
    TAB_FIRING_CIRCULT = 2
    TAB_MAIN_CIRCULT = 3
    TAB_LOG = 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_tab_buttons = []
        self._setup_window()
        self._setup_tabbar()
        self._setup_stack()
        self._wire_events()
        self._switch_tab(self.TAB_MAIN, self.tab_main)
        
    def _setup_window(self):
        self.setObjectName("FireControl")
        self.resize(1280, 1024)

        from PyQt5.QtGui import QIcon, QPixmap
        pix = QPixmap("ui/resources/Icons/Vietnam.png")
        if not pix.isNull():
            self.setWindowIcon(QIcon(pix))

    def _setup_tabbar(self):
        self.tab_bar = QtWidgets.QWidget(self)
        self.tab_bar.setObjectName("TopTabBar")
        self.tab_bar.setFixedHeight(34)
        qss.set_multiple_property(self.tab_bar, role="top-tab-bar")
        
        self.tab_main = self._make_tab("Điều khiển", 8)
        self.tab_info = self._make_tab("Thông tin", 236)
        self.tab_firing_circult = self._make_tab("Mạch bắn", 464)
        self.tab_main_circult = self._make_tab("Mạch ĐK từ xa", 464 + 220 + 8)
        self.tab_log = self._make_tab("Lịch sử", 692 + 220 + 8)

        self.error_indicator = QtWidgets.QLabel(self.tab_log)
        self.error_indicator.setObjectName("ErrorDot")
        self.error_indicator.hide()
        
    def _setup_stack(self):
        self.stack = QtWidgets.QStackedWidget(self)
        self.stack.setObjectName("MainStack")
        qss.set_multiple_property(self.stack, role="background")

        self.stack.addWidget(MainTab(ui_path="ui/views/main_tab/main_control_tab.ui", parent=self.stack))
        self.stack.addWidget(InfoTab(None, self.stack))
        self.stack.addWidget(FiringCircultTab(None, self.stack))
        self.stack.addWidget(MainCircultTab(None, self.stack))
        self.stack.addWidget(LogTab(parent=self.stack))

    def _make_tab(self, text, x): 
        btn = QtWidgets.QPushButton(text, self.tab_bar) 
        btn.setObjectName("TopTabButton") 
        qss.set_multiple_property(btn, role="top-tab-button", state="") 
        btn.setCursor(Qt.PointingHandCursor) 
        btn.setGeometry(x, 6, 220, 28) 
        btn.raise_() 
        self.all_tab_buttons.append(btn)
        return btn
    
    def _wire_events(self): 
        self.tab_main.clicked.connect( lambda: self._switch_tab(self.TAB_MAIN, self.tab_main) ) 
        self.tab_info.clicked.connect( lambda: self._switch_tab(self.TAB_INFO, self.tab_info) ) 
        self.tab_firing_circult.clicked.connect( lambda: self._switch_tab(self.TAB_FIRING_CIRCULT, self.tab_firing_circult) )  
        self.tab_main_circult.clicked.connect( lambda: self._switch_tab(self.TAB_MAIN_CIRCULT, self.tab_main_circult) )
        self.tab_log.clicked.connect( lambda: self._switch_tab(self.TAB_LOG, self.tab_log) )
        
    def resizeEvent(self, event):
        super().resizeEvent(event)

        tab_h = self.tab_bar.height()
        self.tab_bar.setGeometry(0, 0, self.width(), tab_h)

        self.stack.setGeometry(
            0,
            tab_h,
            self.width(),
            self.height() - tab_h
        )


    def _switch_tab(self, index, active_btn):
        self.stack.setCurrentIndex(index)

        for btn in self.all_tab_buttons:
            qss.set_multiple_property(btn, role="top-tab-button", state="active" if btn == active_btn else "")

        if index == self.TAB_LOG:
            self.error_indicator.hide()



    # # --------------------------------------------------
    # # API cho LogTab
    # # --------------------------------------------------
    # def show_error_indicator(self):
    #     if self.stack.currentIndex() != self.TAB_LOG:
    #         self.error_indicator.show()
            
            
if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    from ui.helpers.qss import load_styles_from_yaml

    app = QApplication(sys.argv)
    load_styles_from_yaml(app, file_name="style_manifest.yaml", base_path="ui/styles")

    win = FireControlUI()
    win.show()

    sys.exit(app.exec_())

