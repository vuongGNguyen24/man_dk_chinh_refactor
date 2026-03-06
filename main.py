
from PyQt5.QtWidgets import QApplication
import sys

from ui.fire_control_ui import FireControlUI
from bootstrap.infrastructure_container import InfrastructureContainer
from bootstrap.modules import ElectricalModule, FireControlModule, SystemMonitorModule, SlopeCorrectionModule, LogModule
from bootstrap.config import ConfigLoader
from application.dto import LogEvent
import ui.helpers.qss as qss

def main():
    app = QApplication(sys.argv)
    
    config_loader = ConfigLoader("bootstrap/config/communication.yaml")
    qss.load_styles_from_yaml(app, "style_manifest.yaml", base_path="ui/styles")
    
    main_window = FireControlUI()
    log_module = LogModule(main_window.log_tab)
    log_module.build()
    
    try:
        infra = InfrastructureContainer(config_loader)
        infra.build()
    except Exception as e:
        log_module.add(LogEvent("ERROR", str(e)))
        
    electrical_module = ElectricalModule(infra, main_window)
    electrical_module.build()
    
    fire_control_module = FireControlModule(infra, main_window)
    fire_control_module.build()
        
    # system_monitor_module = SystemMonitorModule(infra, main_window, config_loader)
    # system_monitor_module.build()
        
        
    try:
        electrical_module.start()
    except Exception as e:
        log_module.add(LogEvent("ERROR", str(e)))
        
    fire_control_module.start()
    infra.start()
    main_window.show()
    sys.exit(app.exec_())
    
        

if __name__ == "__main__":
    main()