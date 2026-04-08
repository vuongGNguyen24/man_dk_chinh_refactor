from typing import List
from application.dto.angle.packet import AnglePacket
class LogPort:
    def on_target_angle_changed(self, launcher_id: str, angle: AnglePacket) -> None:
        raise NotImplementedError("Phương thức on_target_angle_changed chưa được triển khai trong LogPort.")
    
    def on_choice_bullets_changed(self, launcher_id: str, choice_bullets: List[int]) -> None:
        raise NotImplementedError("Phương thức on_choice_bullets_changed chưa được triển khai trong LogPort.")
    
    def on_optoelectronic_distance_changed(self, distance_m: float) -> None:
        raise NotImplementedError("Phương thức on_optoelectronic_distance_changed chưa được triển khai trong LogPort.")
    
    def on_optoelectronic_azimuth_changed(self, azimuth_deg: float) -> None:
        raise NotImplementedError("Phương thức on_optoelectronic_azimuth_changed chưa được triển khai trong LogPort.")
    
    def on_current_angle_changed(self, launcher_id: str, angle: AnglePacket) -> None:
        raise NotImplementedError("Phương thức on_current_angle_changed chưa được triển khai trong LogPort.")