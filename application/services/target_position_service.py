from typing import Dict
import math

from domain.value_objects.point import Point2D
from domain.value_objects.ship import Ship
from domain.value_objects.firing_solution import FiringSolution
from domain.rules import normalize_azimuth_angle
from domain.services.targeting_system import TargetingSystem, FiringTableInterpolator

class TargetPositionService:
    def __init__(self, low_targeting_system: TargetingSystem, high_targeting_system: TargetingSystem):
        self.low_targeting_system = low_targeting_system
        self.high_targeting_system = high_targeting_system
    
    def calculate_target_position(self, distance_optoelectronic: float, azimuth_optoelectronic_deg: float, use_high_table: bool = False) -> Point2D:
        """Tính toán vị trí mục tiêu dựa trên dữ liệu từ quang điện tử."""
        targeting_system = self.high_targeting_system if use_high_table else self.low_targeting_system
        return targeting_system.calculate_target_position(distance_optoelectronic, azimuth_optoelectronic_deg)

    def calculate_range_from_elevation(self, elevation_deg: float) -> float:
        """Nội suy ngược: từ góc tầm (độ) tìm khoảng cách.
        
        Args:
            target_angle_degrees: Góc tầm mục tiêu (độ)
            
        Returns:
            Khoảng cách bắn được (mét)
        """
        targeting_system = self.low_targeting_system
        return targeting_system.calculate_range_from_elevation(elevation_deg)
    
    def calculate_firing_solutions(self, target_position: Point2D, use_high_table: bool = False) -> Dict[str, FiringSolution]:
        """Tính toán giải pháp bắn cho từng khẩu pháo."""
        targeting_system = use_high_table and self.high_targeting_system or self.low_targeting_system
        return targeting_system.calculate_firing_solutions(target_position)
    
    @staticmethod 
    def from_firing_tables(low_table: FiringTableInterpolator, high_table: FiringTableInterpolator) -> 'TargetPositionService':
        return TargetPositionService(TargetingSystem(low_table), TargetingSystem(high_table))