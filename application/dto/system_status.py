from dataclasses import dataclass

@dataclass
class ElectricalPointStatus:
    node_id: str
    has_error: bool
    

@dataclass(frozen=True)
class ElectricalPointStatus:
    point_id: str
    powered: bool