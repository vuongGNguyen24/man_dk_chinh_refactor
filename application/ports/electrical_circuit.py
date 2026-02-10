from typing import Dict, Protocol, List
from abc import ABC, abstractmethod
from application.dto import ElectricalPointStatus

class ElectricalPointInputPort(Protocol, ABC):
    @abstractmethod
    def read_points(self) -> Dict[str, bool]:
        """
        Return:
            {
                "P01": True,
                "P02": False,
                ...
            }
        """
        pass


class ElectricalPointObserverPort(Protocol, ABC):
    @abstractmethod
    def on_points_changed(self, changed: List[ElectricalPointStatus]) -> None:
        pass
