from dataclasses import dataclass
from domain.value_objects.parameter import Parameter, Threshold
@dataclass
class AngleHandler(Parameter):
    """Lớp biểu diễn góc tầm, góc hướng
    
    Có thêm thuộc tính góc mục tiêu"""
    target_value: float = 0.0
    def is_target(self) -> bool:
        return self.target == self.current_value
    
@dataclass
class AngleThreshold(Threshold):
    def is_error(self, param: AngleHandler) -> str:
        """Kiểm tra góc có nằm ở vùng giới hạn

        Args:
            param (AngleHandler): góc cần kiểm tra

        Returns:
            str: "" nếu bình thường
            Lỗi nếu góc nằm ngoài vùng giới hạn
        """
        if self.min_normal <= param.current_value <= self.max_normal:
            return ""
        return f"{param.name}: {param.current_value} nằm ngoài vùng giới hạn"
    