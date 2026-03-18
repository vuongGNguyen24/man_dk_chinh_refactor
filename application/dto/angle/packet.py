from dataclasses import dataclass


@dataclass
class AnglePacket:
    azimuth: float
    elevation: float