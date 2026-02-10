from abc import ABC, abstractmethod
from application.dto import NodeStatus, NodeParameter, ModuleParameter, ModuleStatus

class SystemStatusPort(ABC):

    @abstractmethod
    def present_node_status(self, dto: NodeStatus) -> None:
        pass
    
    @abstractmethod
    def present_node_parameter(self, dto: NodeParameter) -> None:
        pass
    
    @abstractmethod
    def present_module_status(self, dto: ModuleStatus) -> None:
        pass
    
    @abstractmethod
    def present_module_parameter(self, dto: ModuleParameter) -> None:
        pass
