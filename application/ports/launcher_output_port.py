from abc import ABC, abstractmethod
from typing import List

from application.dto.angle.packet import AnglePacket
class LauncherCommandPort(ABC):
    """Port gửi lệnh điều khiển giàn phóng ra bên ngoài"""

    @abstractmethod
    def select_bullets(self, launcher_id: str, bullets: List[int]) -> None:
        """Gửi tín hiệu đạn cho giàn phóng được chỉ định với danh sách đạn được chọn

        Args:
            launcher_id (str): id của giàn phóng
            bullets (List[int]): danh sách đạn được chọn trước khi mapping
        """
        pass
    
    @abstractmethod
    def send_target_angle(self, launcher_id, angle_input_deg: AnglePacket) -> None:
        """Gửi tín hiệu chuyển góc đến các giàn 

        Args:
            launcher_id: id của giàn phóng
            angle_input_deg (AngleInputPacket): packet chứa góc tầm và góc hướng theo độ, ví dụ:
            AngleInputPacket(azimuth=15.1, elevation=20.5)
        """
        pass