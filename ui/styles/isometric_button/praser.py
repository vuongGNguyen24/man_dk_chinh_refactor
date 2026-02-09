from PyQt5.QtGui import QColor
from ui.widgets.components.isometric_buttons.visual_state import IsometricVisualState

def parse_color(value):
    if value.startswith("rgba"):
        nums = value[value.find("(")+1:value.find(")")].split(",")
        return QColor(
            int(nums[0]), int(nums[1]), int(nums[2]), int(nums[3])
        )
    return QColor(value)


class IsometricTheme:

    def __init__(self, path: str):
        import yaml
        with open(path, "r", encoding="utf-8") as f:
            self.data = yaml.safe_load(f)

    def get_state(self, widget_type: str, state: str):
        raw = self.data[widget_type].get(state) \
              or self.data[widget_type]["default"]

        return IsometricVisualState(
            top_color=parse_color(raw["topColor"]),
            border_color=parse_color(raw["borderColor"]),
            text_color=parse_color(raw["textColor"]),
            depth=float(raw.get("depth", 5.0)),
            enabled=(state != "disabled")
        )