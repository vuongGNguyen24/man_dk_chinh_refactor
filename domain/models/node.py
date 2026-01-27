from typing import Dict, List
from domain.models.module import Module
from domain.value_objects.parameter import Parameter
from queue import Queue
import time
MAX_HISTORY_ERROR = 100
MAX_HISTORY_VOLTAGE = 100
class Node:
    """
    Entity + Aggregate Root: Node
    """

    def __init__(self, node_id: int, name: str):
        self.node_id = node_id
        self.name = name

        self.voltage_history: Queue[float] = Queue(MAX_HISTORY_VOLTAGE)
        self.current_voltage: Parameter = Parameter("current_voltage", 0.0, "V")
        
        self.modules: Dict[str, Module] = {}

        self.errors: Queue[str] = Queue(MAX_HISTORY_ERROR)
        self.has_error: bool = False
        self.last_update_time: float = 0
    def set_voltage(self, voltage: Parameter):
        self.current_voltage = voltage
        self.voltage_history.append(voltage.current_value)

    def add_module(self, module: Module):
        self.modules[module.module_id] = module

    def clear_errors(self):
        self.errors.clear()
        self.has_error = False

    def recalculate_status(self):
        """
        Tổng hợp trạng thái node từ các module con
        """

        for module in self.modules.values():
            new_errors = module.evaluate()
            if module.status == "error":
                for error in new_errors:
                    self.errors.put(f"{module.name}: {error}")

        self.has_error = len(self.errors) > 0

