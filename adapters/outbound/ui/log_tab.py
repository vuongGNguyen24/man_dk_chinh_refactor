from application.dto import LogEvent
from application.dto.angle.packet import AnglePacket
from ui.views.log_tab import LogTab
from application.ports.log_port import LogPort
from typing import List
LEVEL_STYLE = {
    "INFO":    ("#3B82F6", "ℹ️"),
    "SUCCESS": ("#10B981", "✅"),
    "WARNING": ("#F59E0B", "⚠️"),
    "ERROR":   ("#EF4444", "❌"),
}

class LogTabAdapter(LogPort):
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
        
    def on_target_angle_changed(self, launcher_id: str, angle: AnglePacket) -> None:
        vietnamese_launcher_id = "trái" if launcher_id == "left" else "phải"
        self.append(LogEvent("INFO", f"Điều khiển giàn {vietnamese_launcher_id} với góc hướng: {angle.azimuth:.2f} với góc tầm: {angle.elevation:.2f}"))
    
    def on_choice_bullets_changed(self, launcher_id: str, choice_bullets: List[int]) -> None:
        vietnamese_launcher_id = "trái" if launcher_id == "left" else "phải"
        log_command = ""
        if choice_bullets:
            log_command = f"Giàn {vietnamese_launcher_id} đã chọn đạn số: {choice_bullets}"
        else:
            log_command = f"Giàn {vietnamese_launcher_id} đã bỏ chọn tất cả đạn"
        self.append(LogEvent("INFO", log_command))
        
    def on_optoelectronic_distance_changed(self, distance_m: float) -> None:
        self.append(LogEvent("INFO", f"Nhận được khoảng cách từ QĐT: {distance_m}"))
    
    def on_optoelectronic_azimuth_changed(self, azimuth_deg: float) -> None:
        self.append(LogEvent("INFO", f"Nhận được góc hướng từ QĐT: {azimuth_deg}"))

