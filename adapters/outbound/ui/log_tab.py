from application.dto import LogEvent
from ui.views.log_tab import LogTab

LEVEL_STYLE = {
    "INFO":    ("#3B82F6", "ℹ️"),
    "SUCCESS": ("#10B981", "✅"),
    "WARNING": ("#F59E0B", "⚠️"),
    "ERROR":   ("#EF4444", "❌"),
}

class LogTabAdapter:
    """
    Adapter chịu trách nhiệm định dạng và in log sự kiện ra giao diện UI tab log.
    """

    def __init__(self, view: LogTab):
        """
        Khởi tạo adapter cho Log tab.
        
        Args:
            view: Giao diện UI (tab) hiển thị log trực quan.
        """
        self.view = view

    def append(self, event: LogEvent):
        """
        Thêm một sự kiện mới vào UI log với định dạng màu sắc tương ứng với cấp độ log.
        
        Args:
            event (LogEvent): Sự kiện chứa thông tin cấp độ và nội dung log.
        """
        color, icon = LEVEL_STYLE.get(
            event.level, ("#94A3B8", "")
        )

        html = (
            f'<span style="color:#94A3B8;">'
            f'[{event.timestamp:%Y-%m-%d %H:%M:%S}]</span> '
            f'<span style="color:{color}; font-weight:bold;">'
            f'{icon} [{event.level}]</span> '
            f'{event.message}'
        )

        self.view.append_html(html)

