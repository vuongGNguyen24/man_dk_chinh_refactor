from application.services.eletrical_circuit_monitor_service import ElectricalPointMonitorService
from adapters.inbound.rs485.electrical_point_adapter import RS485ElectricalPointInputAdapter
from adapters.inbound.udp.electrical_point_adapter import UDPElectricalPointInputAdapter
from adapters.outbound.ui.system_diagram_electrical_observer import SystemDiagramElectricalObserver
from application.dto import ElectricalPointStatus
from infrastructure.udp import UDPSocketManager, UDPServer
from infrastructure.serial import SerialConfig, RS485Transport
from bootstrap.config.bit_mask_to_point_id.load import load_rs485_mapping_from_yaml, load_udp_mapping_from_yaml, load_allow_points_from_yaml
from ui.views.system_diagram import SystemDiagramView
from ui.fire_control_ui import FireControlUI
import ui.helpers.qss as qss
import sys
from PyQt5.QtWidgets import QApplication
import yaml
import time
import adapters.inbound.mock as mock
def load_rs485_config(config_path: str) -> SerialConfig:
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        return SerialConfig.from_dict(config['rs485'])


def main():
    startTime = time.time()
    app = QApplication(sys.argv)
    qss.load_styles_from_yaml(app, "style_manifest.yaml", base_path="ui/styles")
    # udp_server = UDPServer(UDPSocketManager("0.0.0.0", 8888))
    main_window = FireControlUI()
    
    udp_adapter =  mock.MockUDPElectricalPointInputAdapter(load_udp_mapping_from_yaml("bootstrap/config/bit_mask_to_point_id/udp.yaml", 
                                                                         "bootstrap/config/jetson_ip.yaml"))
    
    rs485_adapter = mock.MockRS485ElectricalPointInputAdapter( 
                                                     load_rs485_mapping_from_yaml("bootstrap/config/bit_mask_to_point_id/rs485.yaml"))
    
    
    # system_diagram_view = SystemDiagramView("ui/views/system_diagram/layout/dk_tai_cho.ui", 
    #                                         svg_path='ui/resources/Icons/gnd.svg', 
    #                                         json_connections_path='ui/views/system_diagram/layout/dk_tai_cho_connection_mapping.json')
    fire_circult_diagram_observer = SystemDiagramElectricalObserver(main_window.firing_circult_tab.diagram)
    main_circult_diagram_observer = SystemDiagramElectricalObserver(main_window.main_circult_tab.diagram)
    fire_circult_service = ElectricalPointMonitorService(fire_circult_diagram_observer)
    main_circult_service = ElectricalPointMonitorService(main_circult_diagram_observer)
    
    #make connections
    # udp_server.subscribe(udp_adapter.on_message)
    udp_adapter.subscribe(fire_circult_service.on_udp_snapshot)
    rs485_adapter.subscribe(main_circult_service.on_rs485_snapshot)
    
    udp_adapter.start()
    rs485_adapter.start()
    
    
    main_window.show()
    endTime = time.time()
    print("time elapsed: ", endTime - startTime)
    sys.exit(app.exec_())
    
if __name__ == "__main__":
    main()