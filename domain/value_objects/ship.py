from domain.value_objects.point import Point2D
from typing import List, Tuple
class Ship:
    def __init__(self, length: float = 30, width: float = 10):
        self.length = length
        self.width = width
        
        # Quang điện tử (điểm A) 
        self.optoelectronic = Point2D(width/4, 0)
        
        # Pháo B và C 
        self.cannon_1 = Point2D(-width/2, length/4)  # Pháo bên trái (B)
        self.cannon_2 = Point2D(width/2, length/4)   # Pháo bên phải (C)
    
    def get_optoelectronic(self) -> Point2D:
        """Trả về vị trí của quang điện tử."""
        return self.optoelectronic
    
    def get_cannons(self) -> List[Tuple[str, Point2D]]:
        """Trả về vị trí của các khẩu pháo."""
        return [("cannon_1", self.cannon_1), ("cannon_2", self.cannon_2)]