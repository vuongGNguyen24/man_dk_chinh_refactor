from domain.value_objects.angle_handler import AngleThreshold
from domain.value_objects.parameter import Threshold

from dataclasses import dataclass

@dataclass
class AngleInputValidator:
    elevation: AngleThreshold
    azimuth: AngleThreshold
    distance: Threshold
    
    
ANGLE_INPUT_VALIDATOR = AngleInputValidator(
            elevation=AngleThreshold(10, 60),
            azimuth=AngleThreshold(-65, 65),
            distance=Threshold(0, 10000))