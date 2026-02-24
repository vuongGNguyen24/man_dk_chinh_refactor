from application.services.eletrical_circuit_monitor_service import ElectricalPointMonitorService
from adapters.inbound.rs485.electrical_point_adapter import RS485ElectricalPointInputAdapter
from adapters.inbound.udp.electrical_point_adapter import UDPElectricalPointInputAdapter
from adapters.ui.system_diagram_electrical_observer import SystemDiagramElectricalObserver
from application.dto import ElectricalPointStatus
from infrastructure.udp import UDPSocketManager, UDPServer
from infrastructure.serial import SerialConfig, RS485Transport
from bootstrap.config.bit_mask_to_point_id.load import load_rs485_mapping_from_yaml, load_udp_mapping_from_yaml, load_allow_points_from_yaml
from ui.views.system_diagram import SystemDiagramView
import ui.helpers.qss as qss
import sys
from PyQt5.QtWidgets import QApplication
import yaml

def load_rs485_config(config_path: str) -> SerialConfig:
    with open(config_path) as f:
        config = yaml.load(f, Loader=yaml.FullLoader)
        return SerialConfig.from_dict(config['rs485'])


def main():
    app = QApplication(sys.argv)
    qss.load_styles_from_yaml(app, "style_manifest.yaml", base_path="ui/styles")
    udp_server = UDPServer(UDPSocketManager("0.0.0.0", 8888))
    
    udp_adapter = UDPElectricalPointInputAdapter(udp_server, 
                                                 load_udp_mapping_from_yaml("bootstrap/config/bit_mask_to_point_id/udp.yaml", 
                                                                         "bootstrap/config/jetson_ip.yaml"))
    
    rs485_adapter = RS485ElectricalPointInputAdapter(load_rs485_config("bootstrap/config/communicaion.yaml"), 
                                                     load_rs485_mapping_from_yaml("bootstrap/config/bit_mask_to_point_id/rs485.yaml"))
    
    system_diagram_view = SystemDiagramView("ui/views/system_diagram/layout/dk_tai_cho.ui", 
                                            svg_path='ui/resources/Icons/gnd.svg', 
                                            json_connections_path='ui/views/system_diagram/layout/dk_tai_cho_connection_mapping.json')
    system_diagram_observer = SystemDiagramElectricalObserver(system_diagram_view)
    service = ElectricalPointMonitorService(system_diagram_observer, {
        'rs485': load_allow_points_from_yaml("bootstrap/config/bit_mask_to_point_id/rs485.yaml"),
        'udp': load_allow_points_from_yaml("bootstrap/config/bit_mask_to_point_id/udp.yaml"),
    })
    
    
    #make connections
    udp_server.subscribe(udp_adapter.on_message)
    udp_adapter.subscribe(service.on_udp_snapshot)
    rs485_adapter.subscribe(service.on_rs485_snapshot)
    
    
    system_diagram_view.show()
    app.exec_()
    
if __name__ == "__main__":
    main()