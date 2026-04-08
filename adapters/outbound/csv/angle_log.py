import csv
import os
import time
from pathlib import Path
from application.dto.angle.packet import AnglePacket
from application.ports.log_port import LogPort
class CSVAngleLogAdapter(LogPort):
    def __init__(self, folder_path: str, log_interval: float = 1.0):
        self.folder_path = Path(folder_path)
        self.folder_path.mkdir(parents=True, exist_ok=True)
        
        self.log_interval = log_interval
        self.last_log_time = 0
        self.start_time = time.time()
        
        # Giải quyết vấn đề ghi đè do thiếu RTC
        self.file_path = self._generate_unique_filename()
        
        # Khởi tạo file và ghi Header
        self._initialize_file()

    def _generate_unique_filename(self) -> Path:
        """Tạo tên file dạng angle_log_001.csv, tự tăng số để tránh trùng"""
        i = 1
        while True:
            filename = self.folder_path / f"angle_log_{i:03d}.csv"
            if not filename.exists():
                return filename
            i += 1

    def _initialize_file(self):
        with open(self.file_path, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["time", "azimuth", "elevation"])

    def on_target_angle_changed(self, launcher_id: str, angle: AnglePacket):
        self._append_angle_packet(angle)
    def clear_logs(self):
        """Xóa tất cả file log cũ trong thư mục"""
        for file in self.folder_path.glob("angle_log_*.csv"):
            file.unlink()
    
    def _append_angle_packet(self, angle_packet: AnglePacket):
        now = time.time()
        if now - self.last_log_time < self.log_interval:
            return

        elapsed_time = now - self.start_time
        
        # Ghi trực tiếp xuống đĩa (Append mode 'a')
        with open(self.file_path, mode='a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([round(elapsed_time, 2), angle_packet.azimuth, angle_packet.elevation])
            
            # Ép hệ thống đẩy dữ liệu từ đệm xuống đĩa ngay lập tức
            f.flush()
            os.fsync(f.fileno()) 

        self.last_log_time = now