import math
from typing import List, Dict, Optional
import numpy as np

from domain.value_objects.point import Point2D
from domain.value_objects.ship import Ship
from domain.value_objects.firing_solution import FiringSolution
from domain.rules import normalize_azimuth_angle


class FiringTableInterpolator:
    """
    Nội suy bảng bắn theo khoảng cách.

    Domain-level service:
    - Không phụ thuộc CSV
    - Không phụ thuộc pandas
    - Không biết schema cụ thể
    """

    def __init__(
        self,
        ranges: np.ndarray,
        angle_mils: np.ndarray,
        extra_fields: Optional[Dict[str, np.ndarray]] = None,
    ):
        if len(ranges) != len(angle_mils):
            raise ValueError("ranges và angle_mils phải cùng chiều")

        self.ranges = np.asarray(ranges)
        self.angle_mils = np.asarray(angle_mils)
        self.extra_fields = extra_fields or {}

        # sort theo range
        order = np.argsort(self.ranges)
        self.ranges = self.ranges[order]
        self.angle_mils = self.angle_mils[order]

        for k, v in self.extra_fields.items():
            self.extra_fields[k] = np.asarray(v)[order]

    def _interp(self, x: float, y: np.ndarray, z: np.ndarray) -> float:
        if x < z[0]:
            return np.interp(x, z[:2], y[:2])
        if x > self.ranges[-1]:
            return np.interp(x, z[-2:], y[-2:])
        return float(np.interp(x, z, y))

    def elevation_mils(self, range_m: float) -> float:
        return self._interp(range_m, self.angle_mils, self.ranges)

    def elevation_deg(self, range_m: float) -> float:
        return self.elevation_mils(range_m) * 0.06

    def range(self, elevation_deg: float) -> float:
        return self._interp(elevation_deg, self.ranges, self.angle_mils)
    
    def value(self, field: str, range_m: float) -> float:
        """
        Tra một đại lượng hiệu chỉnh theo range.

        Ví dụ:
            table.value("delta_Xwhx", 1200)
        """
        data = self.extra_fields.get(field)
        if data is None:
            return 0.0
        return self._interp(range_m, data)


class TargetingSystem:
    """Hệ thống nhắm mục tiêu tính toán giải pháp bắn."""

    def __init__(self, interpolator: FiringTableInterpolator, ship=Ship()):
        self.ship = ship
        self.interpolator = interpolator

    def calculate_target_position(self, distance_optoelectronic: float, azimuth_optoelectronic_deg: float) -> Point2D:
        """Tính toán vị trí mục tiêu dựa trên dữ liệu từ quang điện tử."""
        optoelectronic_pos = self.ship.get_optoelectronic()
        
        # Tính toán tọa độ x, y của mục tiêu
        azimuth_rad = math.radians(azimuth_optoelectronic_deg)
        target_x = optoelectronic_pos.x + distance_optoelectronic * math.sin(azimuth_rad)
        target_y = optoelectronic_pos.y + distance_optoelectronic * math.cos(azimuth_rad)
        
        return Point2D(target_x, target_y)

    def calculate_range_from_elevation(self, elevation_deg: float) -> float:
        """Nội suy ngược: từ góc tầm (độ) tìm khoảng cách.
        
        Args:
            target_angle_degrees: Góc tầm mục tiêu (độ)
            
        Returns:
            Khoảng cách bắn được (mét)
        """
        return self.interpolator.range(elevation_deg)
    
    def calculate_firing_solutions(self, target_position: Point2D) -> Dict[str, FiringSolution]:
        """Tính toán giải pháp bắn cho từng khẩu pháo."""
        solutions = dict()
        
        for cannon_name, cannon_pos in self.ship.get_cannons():
            distance_to_target = cannon_pos.distance(target_position)
            
            # Tính góc hướng của mục tiêu so với pháo
            delta_x = target_position.x - cannon_pos.x
            delta_y = target_position.y - cannon_pos.y
            
            # Tính góc bằng atan2 để xử lý đúng các góc phần tư
            azimuth_rad = math.atan2(delta_x, delta_y)
            azimuth_deg = math.degrees(azimuth_rad)
            azimuth_deg = normalize_azimuth_angle(azimuth_deg)
            
            elevation_angle_deg = self.interpolator.elevation_deg(distance_to_target)
            
            solutions[cannon_name] = FiringSolution(float(distance_to_target), float(azimuth_deg), float(elevation_angle_deg))
        return solutions