def normalize_azimuth_angle(azimuth_deg: float) -> float:
    while azimuth_deg > 180:
        azimuth_deg -= 360
    while azimuth_deg < -180:
        azimuth_deg += 360
    return azimuth_deg