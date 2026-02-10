from typing import Union

from domain.services.slope_correction_service import SlopeCorrectionService
from domain.services.targeting_system import FiringTableInterpolator
from application.dto import CorrectionInput, CorrectionResult


class CorrectionApplicationService:
    def __init__(
        self,
        interpolator: FiringTableInterpolator,
        slope_service: Union[SlopeCorrectionService, None] = None,
    ):
        self.interpolator = interpolator
        self.slope_service = slope_service

    def calculate(
        self,
        input: CorrectionInput,
        distance_left: float,
        distance_right: float,
        elev_left_deg: float,
        elev_right_deg: float,
    ) -> CorrectionResult:
        # --- Tra bảng ---
        def elev_corr(range_m, std_elev_deg):
            delta = self.interpolator.value("delta_XT", range_m) * (input.air_temp - input.std_temp)
            delta += self.interpolator.value("delta_XH", range_m) * (input.air_pressure - input.std_pressure)
            return delta

        elev_l = elev_corr(distance_left, elev_left_deg)
        elev_r = elev_corr(distance_right, elev_right_deg)

        # --- Chênh tà ---
        if self.slope_service and input.slope_angle != 0:
            elev_l += self.slope_service.interpolate(
                input.slope_angle, elev_left_deg / 0.05625
            ) * 0.05625

            elev_r += self.slope_service.interpolate(
                input.slope_angle, elev_right_deg / 0.05625
            ) * 0.05625

        return CorrectionResult(
            elev_left_deg=elev_l,
            elev_right_deg=elev_r,
            dir_left_deg=0.0,
            dir_right_deg=0.0,
        )
