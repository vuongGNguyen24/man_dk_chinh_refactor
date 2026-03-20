from typing import Optional

from ui.views.angle_input.angle_input_view import AngleInputView
from application.services import FiringControlService
from ui.views.angle_input.angle_input_view import InputType, ControlMode


class AngleInputAdapter:
    """
    Inbound Adapter – UI → Application

    Responsibility:
    - Listen to AngleInputView signals
    - Extract validated input from view
    - Translate UI state into application use-case calls

    This adapter is the only place that depends on PyQt.
    """

    def __init__(
        self,
        view: AngleInputView,
        service: FiringControlService,
        launcher_id: str,
    ):
        self._view = view
        self._service = service
        self._launcher_id = launcher_id

        self._wire()

    # =========================================================
    # Wiring
    # =========================================================

    def _wire(self) -> None:
        self._view.accepted.connect(self._on_accepted)
        self._view.rejected.connect(self._on_rejected)
         # Realtime update
        self._view.distanceInput.lineEdit().textChanged.connect(
            self._on_distance_changed
        )
        self._view.elevationInput.lineEdit().textChanged.connect(
            self._on_elevation_changed
        )

    # =========================================================
    # Handlers
    # =========================================================

    def _on_accepted(self) -> None:
        """
        Called when user presses OK.
        """
        azimuth_deg, elevation_deg, distance_m = None, None, None
        # ---- Direction ----
        if self._view.direction_control_mode == ControlMode.MANUAL:
            azimuth_text = self._view.directionInput.text()
            if not azimuth_text:
                return
            azimuth_deg = float(azimuth_text)
        else:
            # AUTO mode: dùng giá trị hiện tại từ optoelectronic state
            azimuth_deg = self._service.optoelectronics_state.azimuth.current_value

        # ---- Primary input ----
        if self._view.modeInputContainer.mode == InputType.DISTANCE:
            distance_text = self._view.distanceInput.text()
            if not distance_text:
                return
            
            distance_m = float(distance_text)
            
            try:
                elevation_deg = float(self._view.elevationDmsLabel.text())
            except ValueError:
                return
            
            self._service.set_target_angle(self._launcher_id, azimuth_deg, elevation_deg, distance_m)

        else:
            elevation_text = self._view.elevationInput.text()
            if not elevation_text:
                return
            
            try:
                distance_m = float(self._view.distancePreviewLabel.text())
            except ValueError:
                return
            
            elevation_deg = float(elevation_text)
            self._service.set_target_angle(self._launcher_id, azimuth_deg, elevation_deg, distance_m)

    def _on_rejected(self) -> None:
        """
        Optional: close dialog, reset state, etc.
        """
        pass
    
    def _on_distance_changed(self, text: str) -> None:
        def set_empty():
            self._view.elevationDmsLabel.setText("--")
            self._view.elevationDecimalLabel.setText("--")
        if not text:
            set_empty()
            return

        try:
            distance_m = float(text)
        except ValueError:
            set_empty()
            return

        
        def deg_to_lizard(deg: float) -> float:
            #360 deg -> 6000 lizard
            return deg * 6000 / 360
        # # Gọi service để tính toán preview
        caculate_elevation_deg = self._service.compute_firing_solution(
            launcher_id=self._launcher_id,
            distance_m=distance_m,
            use_high_table=self._view.highTableRadio.isChecked(),
        ).elevation

        self._view.elevationDmsLabel.setText(f"{caculate_elevation_deg:.2f}")
        self._view.elevationDecimalLabel.setText(f"{deg_to_lizard(caculate_elevation_deg):.2f}")
        
    def _on_elevation_changed(self, text: str) -> None:
        def set_empty():
            self._view.distancePreviewLabel.setText("--")
        if not text:
            set_empty()
            return

        try:
            elevation_deg = float(text)
        except ValueError:
            set_empty()
            return


        distance_m = self._service.targeting_system.calculate_range_from_elevation(elevation_deg)

        self._view.distancePreviewLabel.setText(f"{distance_m:.2f}")
