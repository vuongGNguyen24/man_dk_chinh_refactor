from typing import Optional
from PyQt5.QtCore import QObject

from ui.views.ballistic_calculator.ballistic_calculator_view import BallisticCalculatorWidget
from application.services.correction_application_service import CorrectionApplicationService
from application.services.firing_control_service import FiringControlService
from application.dto.correction import CorrectionInput

class BallisticCalculatorAdapter(QObject):
    """
    Inbound Adapter – UI → Application for Ballistic Calculator
    
    Responsibility:
    - Listen to BallisticCalculatorWidget signals
    - Extract real-time input from the view and map it to CorrectionInput
    - Call CorrectionApplicationService for calculating corrections
    - Update UI fields with calculation results
    """
    
    def __init__(
        self,
        view: BallisticCalculatorWidget,
        correction_service: CorrectionApplicationService,
        firing_control_service: FiringControlService,
    ):
        super().__init__()
        self._view = view
        self._correction_service = correction_service
        self._firing_control_service = firing_control_service
        
        self._wire()
        self._update_standard_values(CorrectionInput.standard())

    def _wire(self) -> None:
        # Wire text changed signals to trigger recalculations
        self._view.windAlongLowInput.textChanged.connect(self._on_input_changed)
        self._view.windAlongHighInput.textChanged.connect(self._on_input_changed)
        self._view.windCrossLowInput.textChanged.connect(self._on_input_changed)
        self._view.windCrossHighInput.textChanged.connect(self._on_input_changed)
        self._view.airPressureInput.textChanged.connect(self._on_input_changed)
        self._view.airTempInput.textChanged.connect(self._on_input_changed)
        self._view.chargeTempInput.textChanged.connect(self._on_input_changed)
        self._view.kacn14Input.textChanged.connect(self._on_input_changed)
        self._view.slopeAngleInput.textChanged.connect(self._on_input_changed)
        
        # Ship location inputs change distance/azimuth, affecting base angles
        self._view.shipDistanceInput.textChanged.connect(self._on_ship_input_changed)
        self._view.shipAzimuthInput.textChanged.connect(self._on_ship_input_changed)
        
        # Reset button to restore standard values
        self._view.resetButton.clicked.connect(self._on_reset)
        
    def _extract_correction_input(self) -> Optional[CorrectionInput]:
        try:
            return CorrectionInput(
                wind_along_low=float(self._view.windAlongLowInput.text()),
                wind_along_high=float(self._view.windAlongHighInput.text()),
                wind_cross_low=float(self._view.windCrossLowInput.text()),
                wind_cross_high=float(self._view.windCrossHighInput.text()),
                air_pressure=float(self._view.airPressureInput.text()),
                air_temp=float(self._view.airTempInput.text()),
                charge_temp=float(self._view.chargeTempInput.text()),
                kacn14=int(self._view.kacn14Input.text()),
                slope_angle=float(self._view.slopeAngleInput.text()) #TODO: get from UI
            )
        except ValueError:
            print("Error: invalid input")
            return None
            
    def _on_input_changed(self) -> None:
        self._calculate_and_update()
        
    def _on_ship_input_changed(self) -> None:
        try:
            distance = float(self._view.shipDistanceInput.text())
            # azimuth = float(self._view.shipAzimuthInput.text() or 0.0)
            
            # Using FiringControlService to compute firing solutions
            firing_solutions = self._firing_control_service.compute_all_firing_solutions(distance_m=distance)
            
            left_solution = firing_solutions.get("left")
            right_solution = firing_solutions.get("right")
            
            if left_solution:
                self._view.defaultElevationLeft.setText(f"{left_solution.elevation:.2f}°")
                self._view.defaultDirectionLeft.setText(f"{left_solution.azimuth:.2f}°")
                self._view.cannonLeftDistanceLabel.setText(f"{left_solution.distance:.2f}")
                
            if right_solution:
                self._view.defaultElevationRight.setText(f"{right_solution.elevation:.2f}°")
                self._view.defaultDirectionRight.setText(f"{right_solution.azimuth:.2f}°")
                self._view.cannonRightDistanceLabel.setText(f"{right_solution.distance:.2f}")
                
            self._calculate_and_update()
        except ValueError:
            pass
            
    def _calculate_and_update(self) -> None:
        correction_input = self._extract_correction_input()
        # print(correction_input)
        if not correction_input:
            return
            
        # try:
            # # We need the base distance and angles. Recompute from ship inputs
        distance = self._firing_control_service.optoelectronics_state.distance.current_value
        
        result = self._correction_service.calculate(
            input=correction_input,
            distance_left=distance,
            distance_right=distance,
            elev_left_deg=float(self._view.defaultElevationLeft.text()[:-1]),
            elev_right_deg=float(self._view.defaultElevationRight.text()[:-1])
        )
        
        # Update the corrected outputs on UI
        # We assume corrections are additions to base angles
        corrected_elev_left =  float(self._view.defaultElevationLeft.text()[:-1]) + result.elev_left_deg
        corrected_elev_right = float(self._view.defaultElevationRight.text()[:-1]) + result.elev_right_deg
        corrected_dir_left = float(self._view.defaultDirectionLeft.text()[:-1]) + result.dir_left_deg
        corrected_dir_right = float(self._view.defaultDirectionRight.text()[:-1]) + result.dir_right_deg

        self._view.correctedElevationLeft.setText(f"{corrected_elev_left:.2f}°")
        self._view.correctedElevationRight.setText(f"{corrected_elev_right:.2f}°")
        self._view.correctedDirectionLeft.setText(f"{corrected_dir_left:.2f}°")
        self._view.correctedDirectionRight.setText(f"{corrected_dir_right:.2f}°")

        # except Exception as e:
        #     # If any mathematical or missing field error, simply skip updating.
        #     pass
            
    def _update_standard_values(self, std_values: CorrectionInput) -> None:
        self._view.stdAirTempInput.setText(str(std_values.air_temp))
        self._view.stdPressureInput.setText(str(std_values.air_pressure))
        self._view.stdChargeTempInput.setText(str(std_values.charge_temp))
        
    def _on_reset(self) -> None:
        std = CorrectionInput.standard()
        # Wind
        self._view.windAlongLowInput.setText(str(std.wind_along_low))
        self._view.windAlongHighInput.setText(str(std.wind_along_high))
        self._view.windCrossLowInput.setText(str(std.wind_cross_low))
        self._view.windCrossHighInput.setText(str(std.wind_cross_high))
        
        # Temp/Pressure
        self._view.airPressureInput.setText(str(std.air_pressure))
        self._view.airTempInput.setText(str(std.air_temp))
        self._view.chargeTempInput.setText(str(std.charge_temp))
        
        # Details
        self._view.kacn14Input.setText(str(std.kacn14))

        
        self._update_standard_values(std)
