from domain.value_objects.angle_handler import AngleThreshold
from domain.value_objects.parameter import Threshold

from dataclasses import dataclass

@dataclass
class AngleInputValidator:
    elevation: AngleThreshold
    azimuth: AngleThreshold
    distance: Threshold