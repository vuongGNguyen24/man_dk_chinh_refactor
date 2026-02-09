import xml.etree.ElementTree as ET
from pathlib import Path

UI_PATH = Path("../../views/system_diagram/layout/system_diagram_fixed.ui")
OUT_PATH = UI_PATH.with_name("system_diagram_snapped.ui")

SNAP_THRESHOLD = 6  # px, tránh snap nhầm


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
    return {
        "x": int(rect.find("x").text),
        "y": int(rect.find("y").text),
        "w": int(rect.find("width").text),
        "h": int(rect.find("height").text),
        "rect": rect,
    }


def set_y(rect_elem, new_y):
    rect_elem.find("y").text = str(new_y)


tree = ET.parse(UI_PATH)
root = tree.getroot()

verticals = []
horizontals = []

# --- Collect lines ---
for widget in root.iter("widget"):
    if widget.attrib.get("class") != "Line":
        continue

    name = widget.attrib.get("name", "")
    if not name.startswith("conn"):
        continue

    orient = get_enum(get_prop(widget, "orientation"))
    geom = get_rect(widget)
    if not geom:
        continue

    entry = {
        "name": name,
        "orient": orient,
        **geom,
    }

    if orient == "Qt::Vertical":
        verticals.append(entry)
    elif orient == "Qt::Horizontal":
        horizontals.append(entry)

snapped = 0

# --- Snap horizontals to nearest vertical ---
for h in horizontals:
    hx0 = h["x"]
    hx1 = h["x"] + h["w"]
    hy = h["y"]

    best_v = None
    best_dist = None

    for v in verticals:
        vx = v["x"]
        vy0 = v["y"]
        vy1 = v["y"] + v["h"]

        # check overlap
        if not (hx0 <= vx <= hx1):
            continue
        if not (vy0 <= hy <= vy1):
            continue

        dist = abs(hy - v["y"])
        if best_dist is None or dist < best_dist:
            best_dist = dist
            best_v = v

    if best_v and best_dist is not None and best_dist <= SNAP_THRESHOLD:
        new_y = best_v["y"]
        if new_y != hy:
            set_y(h["rect"], new_y)
            snapped += 1

tree.write(OUT_PATH, encoding="utf-8", xml_declaration=True)

print(f"✔ Snapped {snapped} horizontal connectors")
print(f"📄 Output: {OUT_PATH}")
