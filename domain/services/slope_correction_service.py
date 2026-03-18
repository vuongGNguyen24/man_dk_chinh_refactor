import numpy as np


class SlopeCorrectionService:
    """
    Domain Service:
    Tra bảng chênh tà 2D (góc tà × ly giác).
    """

    def __init__(
        self,
        slope_angles: np.ndarray,
        elevation_mils: np.ndarray,
        correction_matrix: np.ndarray,
    ):
        """
        slope_angles: shape (N,)
        elevation_mils: shape (M,)
        correction_matrix: shape (N, M)
        """
        self.slope_angles = np.asarray(slope_angles)
        self.elevation_mils = np.asarray(elevation_mils)
        self.matrix = np.asarray(correction_matrix)

        if self.matrix.shape != (len(slope_angles), len(elevation_mils)):
            raise ValueError("Kích thước bảng 2D không hợp lệ")

    def lookup_nearest(self, slope_angle: float, elevation_mils: float) -> float:
        i = np.argmin(np.abs(self.slope_angles - slope_angle))
        j = np.argmin(np.abs(self.elevation_mils - elevation_mils))
        return float(self.matrix[i, j])

    def interpolate(self, slope_angle: float, elevation_mils: float) -> float:
        # Nội suy tuyến tính 2D đơn giản (bilinear)
        i = np.searchsorted(self.slope_angles, slope_angle) - 1
        j = np.searchsorted(self.elevation_mils, elevation_mils) - 1

        i = np.clip(i, 0, len(self.slope_angles) - 2)
        j = np.clip(j, 0, len(self.elevation_mils) - 2)

        x1, x2 = self.slope_angles[i], self.slope_angles[i + 1]
        y1, y2 = self.elevation_mils[j], self.elevation_mils[j + 1]

        q11 = self.matrix[i, j]
        q12 = self.matrix[i, j + 1]
        q21 = self.matrix[i + 1, j]
        q22 = self.matrix[i + 1, j + 1]

        return float(
            q11 * (x2 - slope_angle) * (y2 - elevation_mils)
            + q21 * (slope_angle - x1) * (y2 - elevation_mils)
            + q12 * (x2 - slope_angle) * (elevation_mils - y1)
            + q22 * (slope_angle - x1) * (elevation_mils - y1)
        ) / ((x2 - x1) * (y2 - y1))
