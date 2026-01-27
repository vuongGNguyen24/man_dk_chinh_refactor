from typing import Dict
from domain.services.targeting_system import TargetingSystem
from application.dto import CannonTargetResult

class TargetPositionService:
    def __init__(self, targeting_system: TargetingSystem):
        self.targeting_system = targeting_system

    def update_target_from_optoelectronic(
        self,
        distance_ship_to_target: float,
        azimuth_ship_to_target_deg: float,
    ) -> Dict[str, CannonTargetResult]:
        """
        Use-case:
        - Từ dữ liệu quang điện tử
        - Tính khoảng cách + góc cho từng pháo
        """
        target_position = self.targeting_system.calculate_target_position(
            distance_ship_to_target,
            azimuth_ship_to_target_deg,
        )

        solutions = self.targeting_system.calculate_firing_solutions(target_position)

        results = {}
        for cannon_name, solution in zip(
            [c[0] for c in self.targeting_system.ship.get_cannons()],
            solutions,
        ):
            results[cannon_name] = CannonTargetResult(
                distance=solution.distance,
                azimuth_deg=solution.azimuth,
                elevation_deg=solution.elevation,
            )

        return results
