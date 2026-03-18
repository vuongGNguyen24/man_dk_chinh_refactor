import xml.etree.ElementTree as ET
from pathlib import Path
import argparse



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

def process_ui(input_path, output_path):
    path = Path(input_path)
    tree = ET.parse(path)
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

        cx = x + w // 2
        cy = y + h // 2

        if orientation == "Qt::Vertical":
            # đường dọc → width = 1, giữ center X
            if w != 1:
                new_x = cx
                new_y = y
                set_rect(geom["rect"], new_x, new_y, 1, h)
                fixed += 1

        elif orientation == "Qt::Horizontal":
            # đường ngang → height = 1, giữ center Y
            if h != 1:
                new_x = x
                new_y = cy
                set_rect(geom["rect"], new_x, new_y, w, 1)
                fixed += 1

    tree.write(path.with_name(output_path), encoding="utf-8", xml_declaration=True)

    print(f"✔ Đã sửa {fixed} line connectors")
    print(f"📄 Output: {output_path}")
    
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Fix conn lines in Qt .ui file"
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
    args = parser.parse_args()
    process_ui(
        args.input,
        args.output,
    )

if __name__ == "__main__":
    main()