from dataclasses import dataclass

@dataclass(frozen=True)
class CannonTargetResult:
    distance: float
    azimuth_deg: float
    elevation_deg: float
