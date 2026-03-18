import xml.etree.ElementTree as ET
from pathlib import Path

def clean_ui_styles(ui_path: str, backup=True):
    ui_path = Path(ui_path)

    if backup:
        backup_path = ui_path.with_suffix(".ui.bak")
        backup_path.write_text(ui_path.read_text(encoding="utf-8"), encoding="utf-8")

    tree = ET.parse(ui_path)
    root = tree.getroot()

    removed = 0

    # tìm tất cả property name="styleSheet"
    for prop in root.findall(".//property[@name='styleSheet']"):
        parent = prop.getparent() if hasattr(prop, "getparent") else None

        # xml.etree không có getparent → xử lý thủ công
        for widget in root.findall(".//widget"):
            if prop in list(widget):
                widget.remove(prop)
                removed += 1
                break

    tree.write(ui_path, encoding="utf-8", xml_declaration=True)
    print(f"✔ Removed {removed} styleSheet entries from {ui_path}")

# ======================
# USAGE
# ======================
clean_ui_styles("ui/views/system_diagram/layout/system_diagram.ui")
