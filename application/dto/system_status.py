from dataclasses import dataclass
from domain.value_objects import Parameter

@dataclass
class NodeStatus:
    node_id: str
    has_error: bool
    
    
@dataclass
class NodeParameter:
    node_id: str
    voltage: Parameter
    
    
@dataclass
class ModuleStatus:
    module_id: str
    has_error: bool
    
    
@dataclass
class ModuleParameter:
    module_id: str
    value: Parameter


@dataclass(frozen=True)
class ElectricalPointStatus:
    point_id: str
    powered: bool
    