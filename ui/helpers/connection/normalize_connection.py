import xml.etree.ElementTree as ET
from pathlib import Path

UI_PATH = Path("../views/system_diagram/layout/system_diagram.ui")
OUT_PATH = UI_PATH.with_name("system_diagram_fixed.ui")


def get_prop(widget, name):
    for prop in widget.findall("property"):
        if prop.attrib.get("name") == name:
            return prop
    return None


def get_enum(prop):
    if prop is None:
        return None
    enum = prop.find("enum")
    return enum.text if enum is not None else None


def get_rect(widget):
    geom = get_prop(widget, "geometry")
    if geom is None:
        return None
    rect = geom.find("rect")
    if rect is None:
        return None
    return {
        "x": int(rect.find("x").text),
        "y": int(rect.find("y").text),
        "w": int(rect.find("width").text),
        "h": int(rect.find("height").text),
        "rect": rect,
    }


def set_rect(rect_elem, x, y, w, h):
    rect_elem.find("x").text = str(x)
    rect_elem.find("y").text = str(y)
    rect_elem.find("width").text = str(w)
    rect_elem.find("height").text = str(h)


tree = ET.parse(UI_PATH)
root = tree.getroot()

fixed = 0

for widget in root.iter("widget"):
    if widget.attrib.get("class") != "Line":
        continue

    name = widget.attrib.get("name", "")
    if not name.startswith("conn"):
        continue

    orient_prop = get_prop(widget, "orientation")
    orientation = get_enum(orient_prop)

    geom = get_rect(widget)
    if geom is None:
        continue

    x, y, w, h = geom["x"], geom["y"], geom["w"], geom["h"]

    if orientation == "Qt::Vertical":
        # đường dọc → width = 1
        if w != 1:
            set_rect(geom["rect"], x, y, 1, h)
            fixed += 1

    elif orientation == "Qt::Horizontal":
        # đường ngang → height = 1
        if h != 1:
            set_rect(geom["rect"], x, y, w, 1)
            fixed += 1

tree.write(OUT_PATH, encoding="utf-8", xml_declaration=True)

print(f"✔ Đã sửa {fixed} line connectors")
print(f"📄 Output: {OUT_PATH}")