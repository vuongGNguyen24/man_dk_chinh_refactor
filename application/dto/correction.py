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
    
    @staticmethod
    def standard() -> 'CorrectionInput':
        return CorrectionInput(
            wind_along_low=0.0,
            wind_along_high=0.0,
            wind_cross_low=0.0,
            wind_cross_high=0.0,
            air_pressure=750,
            air_temp=15.9,
            charge_temp=15,
            kacn14=0,
            slope_angle=0.0,
        )


@dataclass(frozen=True)
class CorrectionResult:
    elev_left_deg: float
    elev_right_deg: float
    dir_left_deg: float
    dir_right_deg: float
