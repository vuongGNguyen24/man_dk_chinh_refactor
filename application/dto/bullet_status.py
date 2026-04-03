from dataclasses import dataclass
from typing import List
@dataclass 
class LauncherBulletStatus:
    loaded: List[bool]
    selected: List[bool]

    def __len__(self):
        assert len(self.loaded) == len(self.selected)
        return len(self.loaded)
