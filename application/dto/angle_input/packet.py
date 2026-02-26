from dataclasses import dataclass


@dataclass
class AngleInputPacket:
    azimuth: float
    elevation: float