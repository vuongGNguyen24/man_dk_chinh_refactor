# domain/models/module.py
from typing import Dict, List
from domain.value_objects.parameter import Parameter, Threshold


class Module:
    """
    Entity: Module tồn tại lâu dài, có identity.
    """

    def __init__(self, module_id: str, name: str, thresholds: Dict[str, Threshold]):
        self.module_id = module_id
        self.name = name
        self.thresholds = thresholds
        self.parameters: Dict[str, Parameter] = {}
        self.errors_history: List[str] = []
        self.status: str = "normal"


    def update_parameter(self, param: Parameter):
        self.parameters[param.name] = param

    def clear_errors(self):
        self.errors_history.clear()

    def evaluate(self) -> List[str]:
        """Kiểm tra một module có an toàn không, dựa vào ngưỡng của các thông số, log lỗi nếu có
            Returns:
                Danh sách lỗi mới
        """
        thresholds = self.thresholds
        new_errors = []
        for name, param in self.parameters.items():
            if name not in thresholds:
                continue

            threshold = thresholds[name]
            is_error = threshold.is_error(param.current_value)
            
            if is_error:
                new_errors.append(is_error)
                self.set_status("error")
        return new_errors
    def set_status(self, status: str):
        self.status = status

