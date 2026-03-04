
from PyQt5.QtWidgets import QApplication
import sys

from ui.fire_control_ui import FireControlUI
from bootstrap.infrastructure_container import InfrastructureContainer
from bootstrap.modules import ElectricalModule, FireControlModule, SystemMonitorModule, SlopeCorrectionModule
from bootstrap.config import ConfigLoader
import ui.helpers.qss as qss

def main():
    app = QApplication(sys.argv)
    qss.load_styles_from_yaml(app, "style_manifest.yaml", base_path="ui/styles")
    main_window = FireControlUI()
    config_loader = ConfigLoader("bootstrap/config/communication.yaml")
    infra = InfrastructureContainer(config_loader)
    infra.build()
    
    electrical_module = ElectricalModule(infra, main_window)
    electrical_module.build()
    
    fire_control_module = FireControlModule(infra, main_window, config_loader)
    fire_control_module.build()
    
    # system_monitor_module = SystemMonitorModule(infra, main_window, config_loader)
    # system_monitor_module.build()
    
    # slope_correction_module = SlopeCorrectionModule(infra, main_window, config_loader)
    # slope_correction_module.build()
    
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()