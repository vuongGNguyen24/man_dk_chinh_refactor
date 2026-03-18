from bootstrap.infrastructure_container import InfrastructureContainer
from ui.fire_control_ui import FireControlUI

from application.services.firing_control_service import FiringControlService
from application.services.target_position_service import TargetPositionService
import adapters.inbound.mock as mock

import bootstrap.config.load.firing_table_path as load_firing_table_path
from adapters.inbound.csv.firing_table_adapter import load_firing_table
from adapters.inbound.udp.launcher_input_adapter import UDPLauncherInputAdapter
from adapters.inbound.can.launcher_input_adapter import CANLauncherInputAdapter
from adapters.inbound.ui import AngleInputAdapter, BulletChoiceInputAdapter
from adapters.inbound.ui.ballistic_calculator_adapter import BallisticCalculatorAdapter

from adapters.outbound.ui.firing_adapter import FiringWidgetAdapter
from adapters.outbound.udp.launcher_command_adapter import UDPLauncherCommandAdapter
from adapters.outbound.can.launcher_command_adapter import CANLauncherCommandAdapter
from application.services.correction_application_service import CorrectionApplicationService
from domain.services.targeting_system import FiringTableInterpolator

#use CAN adapter instead of UDP adapter for angle and bullet input and output command
class FireControlModule:
    def __init__(self, infra: InfrastructureContainer, main_window: FireControlUI):
        self.infra = infra
        self.main_window = main_window
    
    def _build_inbound_adapters(self):
        # self.udp_adapter = UDPLauncherInputAdapter(self.infra.udp_server)
        self.can_adapter = CANLauncherInputAdapter(self.infra.can_server)
    
    def _wire(self):
        
        self.infra.can_server.subscribe(self.can_adapter.on_message)
        self.can_adapter.subscribe(self.fire_service.on_hardware_event)
    def build(self):
        firing_table_paths = load_firing_table_path.from_yaml("bootstrap/config/firing_table_path.yaml")
        
        # hardware adapters
        self._build_inbound_adapters()
        
        # observers
        firing_widget_observer = FiringWidgetAdapter(self.main_window.main_tab)
        # self.output_port = UDPLauncherCommandAdapter(self.infra.udp_server, "127.0.0.1", 9600)
        self.output_port = CANLauncherCommandAdapter(self.infra.can_server)
        # services
        self.targeting_system = TargetPositionService.from_firing_tables(load_firing_table(firing_table_paths['low_table']),
                                                      load_firing_table(firing_table_paths['high_table']))
        self.fire_service = FiringControlService(input_port=self.can_adapter, 
                                                 output_port=self.output_port, 
                                                 targeting_system=self.targeting_system,
                                                 firing_status_observer=firing_widget_observer)
        for launcher_id, launcher in self.fire_service.launchers.items():
            from domain.value_objects.bullet_status import BulletStatus
            tmp = [launcher.get_bullet_status(i) == BulletStatus.LOADED for i in range(1, launcher.num_ammo + 1)]
            self.main_window.main_tab.bullet_widget.update_launcher(launcher_id, tmp, {})
        # ui inbound adapters
        self.left_angle_input_adapter = AngleInputAdapter(self.main_window.main_tab.angle_input_widget_left, self.fire_service, "left")
        self.right_angle_input_adapter = AngleInputAdapter(self.main_window.main_tab.angle_input_widget_right, self.fire_service, "right")
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
        self.infra.udp_server.start()
        
        