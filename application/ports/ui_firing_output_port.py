from abc import ABC, abstractmethod
from typing import List
from domain.value_objects.bullet_status import BulletStatus

from application.dto.angle.packet import AnglePacket

class FiringStatusOutputPort(ABC):

    @abstractmethod
    def on_bullet_status_changed(self, statuses: List[BulletStatus]) -> None:
        pass
    
    @abstractmethod
    def on_target_angle_and_distance_changed(self, launcher_id: str, angle: AnglePacket, distance_m: float) -> None:
        pass
    
    @abstractmethod
    def on_current_angle_changed(self, launcher_id: str, angle: AnglePacket) -> None:    
        pass
    
    @abstractmethod
    def on_distance_input_changed(self, launcher_id: str, distance_m: float) -> None:
        pass