from dataclasses import dataclass
from domain.value_objects.parameter import Parameter

@dataclass
class OptoelectronicsState:
    azimuth: Parameter = Parameter("azimuth", 0, "°")
    distance: Parameter = Parameter("distance", 0, "m")