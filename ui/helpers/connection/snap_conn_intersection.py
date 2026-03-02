import xml.etree.ElementTree as ET
from pathlib import Path

# UI_PATH = Path("../../views/system_diagram/layout/system_diagram_fixed.ui")
# OUT_PATH = UI_PATH.with_name("system_diagram_snapped.ui")

# SNAP_THRESHOLD = 6  # px, tránh snap nhầm


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

def process_ui(input_path, output_path, snap_threshold):
    path = Path(input_path)
    tree = ET.parse(path)
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

        for v in verticals:
            vx = v["x"]
            vy0 = v["y"]
            vy1 = v["y"] + v["h"]

            # Check horizontal range overlaps vertical x (with tolerance)
            if abs(vx - hx0) <= snap_threshold or abs(vx - hx1) <= snap_threshold:
                # Check vertical range overlaps horizontal y
                if vy0 - snap_threshold <= hy <= vy1 + snap_threshold:
                    new_y = hy
                    new_x = vx

                    # Snap horizontal y to closest vertical segment
                    if abs(hy - vy0) <= snap_threshold:
                        new_y = vy0
                    elif abs(hy - vy1) <= snap_threshold:
                        new_y = vy1

                    if new_y != hy:
                        set_y(h["rect"], new_y)
                        h["y"] = new_y
                        snapped += 1

    # --- Snap verticals to nearest horizontal ---
    for v in verticals:
        vx = v["x"]
        vy0 = v["y"]
        vy1 = v["y"] + v["h"]

        for h in horizontals:
            hx0 = h["x"]
            hx1 = h["x"] + h["w"]
            hy = h["y"]

            if abs(hy - vy0) <= snap_threshold or abs(hy - vy1) <= snap_threshold:
                if hx0 - snap_threshold <= vx <= hx1 + snap_threshold:

                    new_x = vx

                    if abs(vx - hx0) <= snap_threshold:
                        new_x = hx0
                    elif abs(vx - hx1) <= snap_threshold:
                        new_x = hx1

                    if new_x != vx:
                        v["rect"].find("x").text = str(new_x)
                        v["x"] = new_x
                        snapped += 1

    tree.write(path.with_name(output_path), encoding="utf-8", xml_declaration=True)

    print(f"✔ Snapped {snapped} horizontal connectors")
    print(f"📄 Output: {output_path}")
    
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Snap conn lines to nearest node QLabel boundary in Qt .ui file"
    )    
    parser.add_argument(
        "-i", "--input",
        required=True,
        help="Input .ui file"
    )
    parser.add_argument(
        "-o", "--output",
        required=True,
        help="Output .ui file"
    )
    parser.add_argument(
        "-t", "--threshold",
        type=int,
        default=6,
        help="Snap distance threshold (default: 6)"
    )
    args = parser.parse_args()
    process_ui(
        args.input,
        args.output,
        args.threshold,
    )
    
if __name__ == "__main__":
    main()