import dataclasses
import math

class Point2D:
    """Lớp biểu diễn điểm trong không gian 2D."""
    
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
    
    def distance(self, other: 'Point2D') -> float:
        """Tính khoảng cách đến một điểm khác."""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)
    
    def __str__(self) -> str:
        return f"({self.x:.2f}, {self.y:.2f})"