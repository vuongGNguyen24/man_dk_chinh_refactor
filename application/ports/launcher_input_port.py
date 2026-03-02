from abc import ABC, abstractmethod
from typing import List, Tuple
from domain.value_objects import BulletStatus


class LauncherInputPort(ABC):
    """
    Port nhận tín hiệu từ bên ngoài liên quan tới giàn phóng
    """

    @abstractmethod
    def on_azimuth_feedback(self):
        """Nhận góc hướng thực tế từ cảm biến
        
        Return: 
            id_launcher: id của giàn phóng trong hệ thống,
            float: góc hướng thực tế từ cảm biến"""
        return 0x12, 0.0

    @abstractmethod
    def on_current_angle_feedback(self):
        """Nhận góc hướng, góc tầm thực tế từ cảm biến
        
        Return: 
            id_launcher: id của giàn phóng trong hệ thống,
            float: góc tầm thực tế từ cảm biến
            float: góc hướng thực tế từ cảm biến"""
        return 0x12, 0.0, 0.0
    
    def on_target_angle_feedback(self):
        """Nhận góc hướng, góc tầm mục tiêu từ cảm biến và giao diện
        
        Return: 
            id_launcher: id của giàn phóng trong hệ thống,
            float: góc hướng mục tiêu từ cảm biến
            float: góc tầm mục tiêu từ cảm biến
        """
        
        return 0x12, 0.0, 0.0
    
    def on_distance_feedback(self) -> float:
        """Nhận khoảng cách thực tế từ cảm biến
            
            Return: 
                float: khoảng cách thực tế từ cảm biến"""
        return 0.0
    
    @abstractmethod
    def on_ammo_status(self) -> Tuple[int, List[BulletStatus]]:
        """Nhận trạng thái của tất cả đạn trong một giàn từ phần cứng
        
        Return: 
            id_launcher: id của giàn phóng trong hệ thống,
            List[BulletStatus]: các trạng thái của tất cả đạn trong một giàn
        """
        return 0x12, [BulletStatus.EMPTY]
