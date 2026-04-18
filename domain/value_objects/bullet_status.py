from enum import Enum
from dataclasses import dataclass
class BulletStatus(Enum):
    EMPTY = "empty"
    LOADED = "loaded"
    SELECTED = "selected"


# @dataclass
# class BulletStatus:
#     is_loaded: bool = False
#     is_selected: bool = False