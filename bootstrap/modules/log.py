from ui.views.log_tab import LogTab
from adapters.outbound.ui.log_tab import LogTabAdapter
from application.dto import LogEvent
class LogModule:
    def __init__(self, log_tab: LogTab):
        self.log_tab = log_tab
    
    def build(self):
        self.adapter = LogTabAdapter(self.log_tab)
        
    def add(self, log_event: LogEvent):
        self.adapter.append(log_event)