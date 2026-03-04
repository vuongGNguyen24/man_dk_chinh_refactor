from application.dto import CorrectionResult, CorrectionInput
from application.services import CorrectionApplicationService
from ui.views.ballistic_calculator import BallisticCalculatorWidget


class BallisticCalculatorAdapter:
    def __init__(
        self,
        view: BallisticCalculatorWidget,
        service: CorrectionApplicationService,
    ):
        self.view = view
        self.service = service
        self.view.resetButton.clicked.connect(self.reset)

    def recalculate(self):
        # 1. Thu thập input
        correction_input = self.view.read_correction_input()
        dist_left, dist_right = self.view.read_distances()
        elev_left, elev_right = self.view.read_base_elevations()

        # 2. Gọi application service
        result = self.service.calculate(
            input=correction_input,
            distance_left=dist_left,
            distance_right=dist_right,
            elev_left_deg=elev_left,
            elev_right_deg=elev_right,
        )

        # 3. Trả kết quả cho UI
        self.view.display_correction_result(result)
        
    def reset(self):
        correction_input = CorrectionInput.standard()
        
        
