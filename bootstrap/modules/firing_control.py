"""
Firing control module for the weapon system.

This module coordinates inbound and outbound adapters, application services,
and UI components to manage firing control logic.
"""

from typing import Optional

# Adapters
import adapters.inbound.mock as mock
from adapters.inbound.can.launcher_input_adapter import CANLauncherInputAdapter
from adapters.inbound.csv.firing_table_adapter import load_firing_table
from adapters.inbound.launcher_input_adapter import LauncherInputAdapter
from adapters.inbound.udp.launcher_input_adapter import UDPLauncherInputAdapter
from adapters.inbound.ui import AngleInputAdapter, BulletChoiceInputAdapter
from adapters.inbound.ui.ballistic_calculator_adapter import BallisticCalculatorAdapter
from adapters.outbound.can.launcher_command_adapter import CANLauncherCommandAdapter
from adapters.outbound.ui.firing_adapter import FiringWidgetAdapter
from adapters.outbound.ui.log_tab import LogTabAdapter

# Application Services
from application.services.correction_application_service import CorrectionApplicationService
from application.services.firing_control_service import FiringControlService
from application.services.target_position_service import TargetPositionService

# Bootstrap and Infrastructure
import bootstrap.config.load.firing_table_path as load_firing_table_path
from bootstrap.infrastructure_container import InfrastructureContainer

# Domain
from domain.services.targeting_system import FiringTableInterpolator

# UI
from ui.fire_control_ui import FireControlUI


class FireControlModule:
    """
    Module responsible for bootstrapping the firing control system.

    It initializes hardware adapters, core services, and UI adapters, 
    and wires them together to form the operational firing control layer.
    """

    def __init__(
        self, 
        infra: InfrastructureContainer, 
        main_window: FireControlUI, 
        log_adapter: Optional[LogTabAdapter] = None
    ):
        """
        Initialize the FireControlModule with necessary dependencies.

        Args:
            infra: Container for infrastructure-level components like servers.
            main_window: The main application UI window.
            log_adapter: Optional adapter for UI logging.
        """
        self.infra = infra
        self.main_window = main_window
        self.log_adapter = log_adapter

    def _build_inbound_adapters(self):
        """Builds inbound adapters for UDP and CAN communication."""
        self.udp_adapter = UDPLauncherInputAdapter(self.infra.udp_server)
        self.can_adapter = CANLauncherInputAdapter(self.infra.can_server)
        self.launcher_input_adapter = LauncherInputAdapter(self.udp_adapter, self.can_adapter)

    def _wire(self):
        """Wires internal subscriptions between infrastructure and services."""
        # Subscribe adapters to raw server messages
        self.infra.can_server.subscribe(self.launcher_input_adapter.can_adapter.on_message)
        self.infra.udp_server.subscribe(self.launcher_input_adapter.udp_adapter.on_message)
        
        # Subscribe service to hardware events distilled by adapters
        self.launcher_input_adapter.can_adapter.subscribe(self.fire_service.on_hardware_event)
        self.launcher_input_adapter.udp_adapter.subscribe(self.fire_service.on_hardware_event)

    def build(self):
        """
        Orchestrates the building process of the firing control system components.

        This involves:
        1. Loading firing table paths.
        2. Constructing communication adapters.
        3. Initializing domain and application services.
        4. Setting up UI-bound observers and adapters.
        5. Finalizing internal connections via wiring.
        """
        firing_table_paths = load_firing_table_path.from_yaml("bootstrap/config/firing_table_path.yaml")
        
        # hardware adapters
        self._build_inbound_adapters()
        
        # observers
        firing_widget_observer = FiringWidgetAdapter(self.main_window.main_tab)
        self.output_port = CANLauncherCommandAdapter(self.infra.can_server)
        
        # services
        self.targeting_system = TargetPositionService.from_firing_tables(
            load_firing_table(firing_table_paths['low_table']),
            load_firing_table(firing_table_paths['high_table'])
        )
        
        self.fire_service = FiringControlService(
            input_port=self.launcher_input_adapter, 
            output_port=self.output_port, 
            targeting_system=self.targeting_system,
            firing_status_observer=firing_widget_observer,
            log_port=self.log_adapter
        )
        
        # Update UI with initial launcher status
        for launcher_id, launcher in self.fire_service.launchers.items():
            from domain.value_objects.bullet_status import BulletStatus
            bullet_states = [
                launcher.get_bullet_status(i) == BulletStatus.LOADED 
                for i in range(1, launcher.num_ammo + 1)
            ]
            self.main_window.main_tab.bullet_widget.update_launcher(launcher_id, bullet_states, {})
            
        # ui inbound adapters
        self.left_angle_input_adapter = AngleInputAdapter(
            self.main_window.main_tab.angle_input_widget_left, 
            self.fire_service, 
            "left"
        )
        self.right_angle_input_adapter = AngleInputAdapter(
            self.main_window.main_tab.angle_input_widget_right, 
            self.fire_service, 
            "right"
        )
        self.bullet_choice_adapter = BulletChoiceInputAdapter(self.main_window.main_tab, self.fire_service)
        
        # correction service
        interpolator = load_firing_table(firing_table_paths['low_table'])
        self.correction_service = CorrectionApplicationService(interpolator=interpolator)

        # ballistic calculator adapter
        self.ballistic_calculator_adapter = BallisticCalculatorAdapter(
            view=self.main_window.main_tab.calculator_widget,
            correction_service=self.correction_service,
            firing_control_service=self.fire_service
        )
        
        self._wire()

    def start(self):
        """Starts the infrastructure servers to begin receiving and sending messages."""
        self.infra.start()
        
        