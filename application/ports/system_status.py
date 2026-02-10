from abc import ABC, abstractmethod
from application.dto import ElectricalPointStatus

class SystemStatusPort(ABC):

    @abstractmethod
    def present_node_status(self, dto: ElectricalPointStatus) -> None:
        pass
