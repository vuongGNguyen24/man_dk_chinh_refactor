import xml.etree.ElementTree as ET
import math
import copy

THRESHOLD = 15  # khoảng cách đủ gần để snap

def get_rect(widget):
    rect = widget.find("./property[@name='geometry']/rect")
    if rect is None:
        return None
    return {
        "x": int(rect.find("x").text),
        "y": int(rect.find("y").text),
        "w": int(rect.find("width").text),
        "h": int(rect.find("height").text),
    }

def set_rect(widget, x, y, w, h):
    rect = widget.find("./property[@name='geometry']/rect")
    rect.find("x").text = str(int(x))
    rect.find("y").text = str(int(y))
    rect.find("width").text = str(int(w))
    rect.find("height").text = str(int(h))

def get_orientation(widget):
    enum = widget.find("./property[@name='orientation']/enum")
    if enum is None:
        return None
    return enum.text  # Qt::Horizontal / Qt::Vertical

def endpoint_snap_to_node(px, py, node_rect):
    nx = node_rect["x"]
    ny = node_rect["y"]
    nw = node_rect["w"]
    nh = node_rect["h"]

    # check left
    if abs(px - nx) < THRESHOLD and ny <= py <= ny + nh:
        return nx, py

    # check right
    if abs(px - (nx + nw)) < THRESHOLD and ny <= py <= ny + nh:
        return nx + nw, py

    # check top
    if abs(py - ny) < THRESHOLD and nx <= px <= nx + nw:
        return px, ny

    # check bottom
    if abs(py - (ny + nh)) < THRESHOLD and nx <= px <= nx + nw:
        return px, ny + nh

    return None

def process_ui(input_path, output_path, threshold):
    global THRESHOLD
    THRESHOLD = threshold
    from pathlib import Path
    path = Path(input_path)
    tree = ET.parse(path)
    root = tree.getroot()

    # collect node labels
    nodes = []
    for widget in root.iter("widget"):
        name = widget.get("name", "")
        cls = widget.get("class", "")
        if cls == "QLabel" and name.startswith("node"):
            rect = get_rect(widget)
            if rect:
                nodes.append(rect)

    # process lines
    for widget in root.iter("widget"):
        name = widget.get("name", "")
        cls = widget.get("class", "")
        if cls == "Line" and name.startswith("conn"):

            rect = get_rect(widget)
            if not rect:
                continue

            orientation = get_orientation(widget)
            x, y, w, h = rect["x"], rect["y"], rect["w"], rect["h"]

            if orientation == "Qt::Horizontal":
                p1 = [x, y + h / 2]
                p2 = [x + w, y + h / 2]
            elif orientation == "Qt::Vertical":
                p1 = [x + w / 2, y]
                p2 = [x + w / 2, y + h]
            else:
                continue

            # snap endpoints
            for node in nodes:
                snap1 = endpoint_snap_to_node(p1[0], p1[1], node)
                if snap1:
                    p1 = list(snap1)

                snap2 = endpoint_snap_to_node(p2[0], p2[1], node)
                if snap2:
                    p2 = list(snap2)

            # update rect from new endpoints
            if orientation == "Qt::Horizontal":
                new_x = min(p1[0], p2[0])
                new_w = abs(p2[0] - p1[0])
                set_rect(widget, new_x, y, new_w, h)

            elif orientation == "Qt::Vertical":
                new_y = min(p1[1], p2[1])
                new_h = abs(p2[1] - p1[1])
                set_rect(widget, x, new_y, w, new_h)

    tree.write(path.with_name(output_path), encoding="utf-8", xml_declaration=True)


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
        default=10,
        help="Snap distance threshold (default: 15)"
    )


    args = parser.parse_args()

    process_ui(
        args.input,
        args.output,
        args.threshold,
    )
    
if __name__ == "__main__":
    main()