from bootstrap.config.bit_mask_to_point_id.load import load_udp_mapping_from_yaml, load_rs485_mapping_from_yaml
from bootstrap.config.load.config_loader import SerialConfig, load_rs485_config
from bootstrap.infrastructure_container import InfrastructureContainer
from ui.fire_control_ui import FireControlUI
from adapters.inbound.rs485.electrical_point_adapter import RS485ElectricalPointInputAdapter
from adapters.inbound.udp.electrical_point_adapter import UDPElectricalPointInputAdapter
from adapters.outbound.ui.system_diagram_electrical_observer import SystemDiagramElectricalObserver
from application.services.eletrical_circuit_monitor_service import ElectricalPointMonitorService
import adapters.inbound.mock as mock


class ElectricalModule:

    def __init__(self, infra:InfrastructureContainer, main_window: FireControlUI):
        self.infra = infra
        self.main_window = main_window

    def _build_inbound_adapters(self):
        self.udp_adapter = UDPElectricalPointInputAdapter(
            load_udp_mapping_from_yaml("bootstrap/config/bit_mask_to_point_id/udp.yaml", 
                                       "bootstrap/config/jetson_ip.yaml"),
        )

        self.rs485_adapter = RS485ElectricalPointInputAdapter(
            load_rs485_config("bootstrap/config/communication.yaml"),
            load_rs485_mapping_from_yaml("bootstrap/config/bit_mask_to_point_id/rs485.yaml"),
        )
        
    def _wire(self):
        self.infra.udp_server.subscribe(self.udp_adapter.on_message)
        self.udp_adapter.subscribe(self.fire_service.on_udp_snapshot)
        self.rs485_adapter.subscribe(self.main_service.on_rs485_snapshot)
    def build(self):

        # hardware adapters
        self._build_inbound_adapters()

        # ui adapters
        
        # observers
        fire_observer = SystemDiagramElectricalObserver(
            self.main_window.firing_circult_tab.diagram
        )

        main_observer = SystemDiagramElectricalObserver(
            self.main_window.main_circult_tab.diagram
        )

        # services
        self.fire_service = ElectricalPointMonitorService(fire_observer)
        self.main_service = ElectricalPointMonitorService(main_observer)

        # wiring
        self._wire()
    def start(self):
        self.infra.udp_server.start()
        # self.udp_adapter.start()
        self.rs485_adapter.start()
        
        
class MockElectricalModule(ElectricalModule):
    def _build_inbound_adapters(self):
        self.udp_adapter = mock.MockUDPElectricalPointInputAdapter(
            load_udp_mapping_from_yaml("bootstrap/config/bit_mask_to_point_id/udp.yaml", 
                                       "bootstrap/config/jetson_ip.yaml"),
        )

        self.rs485_adapter = mock.MockRS485ElectricalPointInputAdapter(
            load_rs485_mapping_from_yaml("bootstrap/config/bit_mask_to_point_id/rs485.yaml"),
        )
        
    def start(self):
        super().start()
        self.udp_adapter.start()
    
    