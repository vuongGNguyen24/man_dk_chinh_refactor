from PyQt5.QtGui import QIntValidator

class BinaryValidator(QIntValidator):
    """Validator chỉ chấp nhận giá trị 0 hoặc 1."""
    
    def __init__(self, parent=None):
        super().__init__(0, 1, parent)
    
    def validate(self, input_str, pos):
        # Chỉ chấp nhận chuỗi rỗng, "0" hoặc "1"
        if input_str == "":
            return (QIntValidator.Intermediate, input_str, pos)
        if input_str in ["0", "1"]:
            return (QIntValidator.Acceptable, input_str, pos)
        return (QIntValidator.Invalid, input_str, pos)