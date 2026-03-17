from typing import List, Tuple
from domain.value_objects import BulletStatus


class LauncherInputPort:

    def subscribe(self, callback):
        pass
    
    def select_bullets(self, launcher_id: str):
        pass
    
    def unselect_bullets(self, launcher_id: str):
        pass
    
    def set_target_angle(self, launcher_id: str, azimuth_deg: float, elevation_deg: float):
        pass
    
    def choose_bullet(self, launcher_id: str, index: int):
        pass
    
    def unchoose_bullet(self, launcher_id: str, index: int):
        pass
    
    def select_all_bullets(self, launcher_id: str):
        pass
    
    def unselect_all_bullets(self):
        pass
