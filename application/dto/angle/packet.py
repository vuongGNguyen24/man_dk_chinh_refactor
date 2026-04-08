from dataclasses import dataclass


@dataclass
class AnglePacket:
    """Gói dữ liệu chứa thông tin về góc hướng (azimuth) và góc tầm (elevation) của mục tiêu."""
    azimuth: float
    elevation: float