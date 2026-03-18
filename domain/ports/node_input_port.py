from abc import ABC, abstractmethod
from typing import Dict

from domain.value_objects.parameter import Parameter


class NodeInputPort(ABC):
    """
    Port nhận dữ liệu từ node phần cứng
    """

    @abstractmethod
    def on_voltage_update(self):
        """Nhận điện áp từ phần cứng

        Return: 
            id_node: id của node trong hệ thống,
            float: điện áp của node
        """
        id_node = 0
        voltage = 0.0
        return id_node, voltage

    @abstractmethod
    def on_module_parameters_update(self) -> Dict[str, Parameter]:
        """Nhận các tham số của module từ phần cứng
        
        Return: 
            id_node: id của node trong hệ thống,
            id_module: id của module trong hệ thống,
            Dict[str, Parameter]: các tham số của module
        """
        id_node = 0
        id_module = 0
        params = {"Voltage": Parameter("Voltage", 0.0, "V"), 
                  "Current": Parameter("Current", 0.0, "A"), 
                  "Temperature": Parameter("Temperature", 0.0, "°C"),
                  "Power": Parameter("Power", 0.0, "W")}
        return id_node, id_module, params
        

