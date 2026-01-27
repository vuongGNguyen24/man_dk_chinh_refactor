from abc import ABC, abstractmethod
from typing import List
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
    def set_target_azimuth(self, launcher_id: str, angle_deg: float) -> None:
        """
        Gửi góc hướng mục tiêu cho giàn phóng
        """
        pass
    @abstractmethod
    def set_target_elevation(self, launcher_id: str, angle_deg: float) -> None:
        """
        Gửi góc tầm mục tiêu cho giàn phóng
        """
        pass
