from typing import Dict, List
from application.dto import ElectricalPointStatus

class ElectricalPointInputPort:
    def read_points(self) -> Dict[str, bool]:
        """
        Return:
            {
                "P01": True,
                "P02": False,
                ...
            }
        """
        raise NotImplementedError


class ElectricalPointObserverPort:
    def on_points_changed(self, changed: List[ElectricalPointStatus]) -> None:
        raise NotImplementedError
