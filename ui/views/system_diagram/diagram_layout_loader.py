"""
Module for loading system diagram layouts from Qt UI files.
This module provides a loader that extracts widget positions and metadata from UI files.
"""

from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QWidget, QFrame, QGroupBox, QApplication, QGraphicsView, QLabel, QPushButton
from typing import Dict
import sys


class DiagramLayoutLoader:
    """
    Loader for system diagram layouts defined in .ui files.

    This class handles loading a UI file and collecting specific widgets (nodes, group boxes,
    connections, etc.) based on their object names and types. It separates the layout
    definition from the rendering and animation logic.

    Attributes:
        root: The loaded root widget from the .ui file.
    """

    def __init__(self, ui_file_path: str):
        """
        Initializes the loader and loads the specified UI file.

        Args:
            ui_file_path: Path to the .ui file to load.
        """
        if QApplication.instance() is None:
            self._app = QApplication(sys.argv)
        else:
            self._app = None

        self.root = loadUi(ui_file_path)

    def __collect_items(self, preifx: str, widget_type: type) -> Dict[str, QWidget]:
        """
        Collects widgets of a specific type whose object names start with a given prefix.

        Args:
            preifx: The object name prefix to filter by.
            widget_type: The Qt widget type to look for.

        Returns:
            A dictionary mapping object names to their corresponding widget instances.
        """
        return {
            w.objectName(): w
            for w in self.root.findChildren(widget_type)
            if w.objectName().startswith(preifx)
        }
    
    def collect_nodes(self) -> Dict[str, QLabel]:
        """
        Collects all node widgets (QLabels starting with 'node').

        Returns:
            Dictionary of node names to QLabel widgets.
        """
        return self.__collect_items("node", QLabel)
    
    def collect_group_boxes(self) -> Dict[str, QGroupBox]:
        """
        Collects all group box widgets (QGroupBoxes starting with 'groupBox').

        Returns:
            Dictionary of group box names to QGroupBox widgets.
        """
        return self.__collect_items("groupBox", QGroupBox)
    
    def collect_connections(self) -> Dict[str, QFrame]:
        """
        Collects all connection placeholder widgets (QFrames starting with 'conn').

        Returns:
            Dictionary of connection names to QFrame widgets.
        """
        return self.__collect_items("conn", QFrame)
    
    def collect_gnd(self) -> Dict[str, QLabel]:
        """
        Collects all ground indicators (QLabels starting with 'gnd').

        Returns:
            Dictionary of ground indicator names to QLabel widgets.
        """
        return self.__collect_items("gnd", QLabel)
    
if __name__ == "__main__":
    loader = DiagramLayoutLoader(r"C:\Users\Admin\Desktop\projects\wm18\man_dk_chinh_refactor\ui\views\system_diagram\layout\system_diagram.ui")
    print(loader.collect_nodes())
    print(loader.collect_group_boxes())
    print(loader.collect_connections())