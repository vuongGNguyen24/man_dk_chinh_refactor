from enum import Enum
class HardwareEventId(str, Enum):
    AMMO_STATUS_LEFT = "ammo_status_left"
    AMMO_STATUS_RIGHT = "ammo_status_right"
    ANGLE_LEFT = "angle_left"
    ANGLE_RIGHT = "angle_right"
    DISTANCE = "distance"
    AZIMUTH = "azimuth"