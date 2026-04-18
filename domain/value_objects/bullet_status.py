from enum import Enum
from dataclasses import dataclass
# class BulletStatus(Enum):
#     EMPTY = "empty"
#     LOADED = "loaded"
#     SELECTED = "selected"


@dataclass
class BulletStatus:
    is_loaded: bool = False
    is_selected: bool = False
    
    @staticmethod
    def empty():
        return BulletStatus(is_loaded=False, is_selected=False)
    def __str__(self):
        return f"BulletStatus(is_loaded={self.is_loaded}, is_selected={self.is_selected})"