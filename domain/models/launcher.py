from dataclasses import dataclass
from typing import List
from domain.value_objects.angle_handler import AngleHandler, AngleThreshold
from domain.value_objects.bullet_status import BulletStatus
# import random
@dataclass
class Launcher:
    """Lớp biểu diễn các trạng thái chính của khẩu pháo."""
    
    num_ammo: int = 18
    azimuth_threshold: AngleThreshold = AngleThreshold(-70, 70, "°")
    elevation_threshold: AngleThreshold = AngleThreshold(12, 65, "°")
    
    def __post_init__(self):
        self.bullets_statuses = [BulletStatus.EMPTY for i in range(self.num_ammo)]
        self.azimuth = AngleHandler("azimuth", 0, "°")
        self.elevation = AngleHandler("elevation", self.elevation_threshold.min_normal, "°")
    
    def __len__(self):
        return self.num_ammo
        
    def get_bullet_status(self, index: int) -> BulletStatus:
        return self.bullets_statuses[index - 1]
    
    def choose_bullet(self, index: int):
        if self.get_bullet_status(index) == BulletStatus.EMPTY:
            raise ValueError(f"Ống phóng {index} chưa có đạn")
        self.set_bullet_status(index, BulletStatus.SELECTED)
        
    def unchoose_bullet(self, index: int):
        if self.get_bullet_status(index) == BulletStatus.EMPTY:
            raise ValueError(f"Ống phóng {index} chưa có đạn")
        self.set_bullet_status(index, BulletStatus.LOADED)
        
    def set_bullet_status(self, index: int, status: BulletStatus):
        self.bullets_statuses[index - 1] = status
    
    # def on_bullet_status_update(self, status: List[BulletStatus]):
    #     """Cập nhật trạng thái đạn hàng loạt

    #     Args:
    #         status (List[BulletStatus]): _description_
    #     """
    #     self.bullets_statuses = status
    
    def set_current_angle(self, azimuth: float, elevation: float):
        self.azimuth.current_value = azimuth   
        self.elevation.current_value = elevation
    
    def set_target_angle(self, azimuth: float, elevation: float):
        self.azimuth.target_value = azimuth
        self.elevation.target_value = elevation