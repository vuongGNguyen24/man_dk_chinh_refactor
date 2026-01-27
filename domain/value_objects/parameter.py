from dataclasses import dataclass

@dataclass
class Parameter:
    """Lớp biểu diễn giá trị đại lượng
    """
    name: str = ""
    current_value: float = 0.0
    unit: str = ""
    
@dataclass(frozen=True)
class Threshold:
    """
    Lớp kiểm tra an toàn của đại lượng
    """
    min_normal: float
    max_normal: float
    unit: str = ""

    def is_error(self, param: Parameter) -> str:
        """Kiểm tra an toàn của đại lượng
        Args:
            value (Parameter): đại lượng cần kiểm tra

        Returns:
            str: "" nếu bình thường
            Lỗi nếu đại lượng nếu không bình thường
        """
        assert self.unit == param.unit
        if self.min_normal <= param.current_value <= self.max_normal:
            return ""
        elif param.current_value < self.min_normal:
            return f"{param.name} thấp, ({param.current_value:.1f}{self.unit} < {self.max_val}{self.unit})"
        else:
            return f"{param.name} cao, ({param.current_value:.1f}{self.unit} > {self.max_val}{self.unit})"
    
    