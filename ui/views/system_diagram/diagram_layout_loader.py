from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QFrame, QGroupBox, QApplication, QGraphicsView, QLabel
from typing import Dict
import sys


class DiagramLayoutLoader:
    """
    UI Component:
    - Đọc layout từ file .ui đã load
    - Thu thập vị trí các node (objectName bắt đầu bằng 'node')
    - Không chứa logic vẽ hay animation
    """

    def __init__(self, ui_file_path: str):
        if QApplication.instance() is None:
            self._app = QApplication(sys.argv)
        else:
            self._app = None

        self.root = loadUi(ui_file_path)

    def __collect_items(self, preifx: str, widget_type: type) -> Dict[str, Dict]:
        """
        Thu thập layout của các widget có objectName bắt đầu bằng prefix

        Returns:
            {
                "prefix_xxx": {
                    left, top, right, bottom,
                    width, height,
                    center_x, center_y
                }
            }
        """
        return {
            w.objectName(): w
            for w in self.root.findChildren(widget_type)
            if w.objectName().startswith(preifx)
        }
    
    def collect_nodes(self) -> Dict[str, Dict]:
        return self.__collect_items("node", QWidget)
    
    def collect_group_boxes(self) -> Dict[str, Dict]:
        return self.__collect_items("groupBox", QGroupBox)
    
    def collect_connections(self) -> Dict[str, Dict]:
        return self.__collect_items("conn", QFrame)
    
    def collect_gnd(self) -> Dict[str, QLabel]:
        return self.__collect_items("gnd", QLabel)
    
if __name__ == "__main__":
    loader = DiagramLayoutLoader("sketech.ui")
    # print(loader.collect_nodes())
    print(loader.collect_group_boxes())
    # print(loader.collect_connections())