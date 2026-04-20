
from PyQt5.QtWidgets import QApplication
import sys

from ui.fire_control_ui import FireControlUI
from bootstrap.infrastructure_container import InfrastructureContainer
from bootstrap.modules.firing_control import MockFireControlModule
from bootstrap.modules.electrical_monitor import MockElectricalModule
from bootstrap.config import ConfigLoader
from application.dto import LogEvent
from adapters.outbound.ui.log_tab import LogTabAdapter
import ui.helpers.qss as qss

def main():
    app = QApplication(sys.argv)
    
    config_loader = ConfigLoader("bootstrap/config/communication.yaml")
    qss.load_styles_from_yaml(app, "style_manifest.yaml", base_path="ui/styles")
    
    main_window = FireControlUI()
    main_window.showFullScreen()
    log_adapter = LogTabAdapter(main_window.log_tab)
    
    try:
        infra = InfrastructureContainer(config_loader)
        infra.build()
    except Exception as e:
        log_adapter.append(LogEvent("ERROR", str(e)))
        
    electrical_module = MockElectricalModule(infra, main_window)
    electrical_module.build()
    
    fire_control_module = MockFireControlModule(infra, main_window, log_adapter=log_adapter)
    fire_control_module.build()
        
    # system_monitor_module = SystemMonitorModule(infra, main_window, config_loader)
    # system_monitor_module.build()
        
        
    try:
        electrical_module.start()
    except Exception as e:
        log_adapter.append(LogEvent("ERROR", str(e)))
    
    try:
        fire_control_module.start()
    except Exception as e:
        log_adapter.append(LogEvent("ERROR", str(e)))
    
    # try:
    #     system_monitor_module.start()
    # except Exception as e:
    #     log_module.append(LogEvent("ERROR", str(e)))
    try:
        infra.start()
    except Exception as e:
        log_adapter.append(LogEvent("ERROR", str(e)))
    main_window.show()
    sys.exit(app.exec_())
    
        

if __name__ == "__main__":
    main()