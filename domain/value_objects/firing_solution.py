from dataclasses import dataclass
@dataclass
class FiringSolution:
    """Lớp biểu diễn giải pháp bắn."""
    distance: float = 0.0
    azimuth: float = 0.0
    elevation: float = 0.0