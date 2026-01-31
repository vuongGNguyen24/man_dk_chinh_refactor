import re
from xml.etree import ElementTree as ET

from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtGui import QPixmap, QPainter, QIcon
from PyQt5.QtCore import Qt, QByteArray, QSize
from PyQt5.QtWidgets import QPushButton

def load_svg_text(svg_path: str) -> str:
    with open(svg_path, "r", encoding="utf-8") as f:
        return f.read()

def recolor_svg(svg_text: str, color: str) -> str:
    # normalize #ffffffff → #ffffff
    if color.startswith("#") and len(color) == 9:
        color = color[:7]

    try:
        root = ET.fromstring(svg_text)

        for elem in root.iter():
            if "fill" in elem.attrib and elem.attrib["fill"].lower() not in ("none", "transparent"):
                elem.attrib["fill"] = color

            if "stroke" in elem.attrib and elem.attrib["stroke"].lower() not in ("none", "transparent"):
                elem.attrib["stroke"] = color

            if "style" in elem.attrib:
                style = elem.attrib["style"]
                style = re.sub(r"fill:\s*[^;]+", f"fill:{color}", style)
                style = re.sub(r"stroke:\s*[^;]+", f"stroke:{color}", style)
                elem.attrib["style"] = style

        return ET.tostring(root, encoding="unicode")

    except Exception:
        return svg_text

def svg_to_pixmap(
    svg_text: str,
    size: QSize,
    alpha: int = 255,
) -> QPixmap:
    if size.width() <= 0 or size.height() <= 0:
        return QPixmap()

    renderer = QSvgRenderer(QByteArray(svg_text.encode("utf-8")))
    if not renderer.isValid():
        return QPixmap()

    pixmap = QPixmap(size)
    pixmap.fill(Qt.transparent)

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    renderer.render(painter)
    painter.end()

    if alpha < 255:
        transparent = QPixmap(size)
        transparent.fill(Qt.transparent)
        painter = QPainter(transparent)
        painter.setOpacity(alpha / 255.0)
        painter.drawPixmap(0, 0, pixmap)
        painter.end()
        pixmap = transparent

    return pixmap

def svg_to_icon(svg_text: str, size: QSize, alpha: int = 255) -> QIcon:
    pixmap = svg_to_pixmap(svg_text, size, alpha)
    return QIcon(pixmap) if not pixmap.isNull() else QIcon()

def apply_svg_icon_to_button(
    button: QPushButton,
    svg_path: str,
    color: str,
    size: QSize,
    alpha: int = 255,
):
    svg_text = load_svg_text(svg_path)
    svg_text = recolor_svg(svg_text, color)
    icon = svg_to_icon(svg_text, size, alpha)

    button.setIcon(icon)
    button.setIconSize(size)
    button.setText("")

