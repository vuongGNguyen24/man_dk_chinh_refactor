from dataclasses import dataclass

@dataclass(frozen=True)
class CorrectionInput:
    wind_along_low: float
    wind_along_high: float
    wind_cross_low: float
    wind_cross_high: float
    air_pressure: float
    air_temp: float
    charge_temp: float
    kacn14: int
    slope_angle: float
    std_temp: float
    std_pressure: float
    std_charge_temp: float


@dataclass(frozen=True)
class CorrectionResult:
    elev_left_deg: float
    elev_right_deg: float
    dir_left_deg: float
    dir_right_deg: float
