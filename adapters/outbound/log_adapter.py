from adapters.outbound.ui.log_tab import LogTabAdapter
from adapters.outbound.csv.angle_log import CSVAngleLogAdapter
from ui.views.log_tab import LogTab


class LogAdapter:
    def __init__(self, ui_adapter: LogTabAdapter, csv_adapter: CSVAngleLogAdapter):
        self.ui_adapter = ui_adapter
        self.csv_adapter = csv_adapter

    def __getattr__(self, name):
        # Nếu gọi một hàm không có trong LogAdapter, 
        # Python sẽ tìm nó trong ui_adapter hoặc csv_adapter
        if hasattr(self.ui_adapter, name):
            return getattr(self.ui_adapter, name)
        if hasattr(self.csv_adapter, name):
            return getattr(self.csv_adapter, name)
        raise AttributeError(f"Không tìm thấy phương thức {name}")