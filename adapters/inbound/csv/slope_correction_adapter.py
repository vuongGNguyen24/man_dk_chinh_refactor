import numpy as np
import pandas as pd
from typing import Union

from domain.services.slope_correction_service import SlopeCorrectionService


class SlopeCorrectionCsvAdapter:
    """
    Outbound Adapter:
    Load slope correction 2D table from CSV and build domain service.
    """

    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def load(self) -> SlopeCorrectionService:
        df = pd.read_csv(self.csv_path)

        if df.shape[1] < 2:
            raise ValueError(
                "CSV phải có ít nhất 2 cột: góc tà + các cột ly giác"
            )

        # Cột đầu tiên: góc tà
        slope_angles = df.iloc[:, 0].to_numpy(dtype=float)

        # Các cột còn lại: ly giác (header phải là số)
        try:
            elevation_mils = np.array(
                [float(col) for col in df.columns[1:]],
                dtype=float
            )
        except ValueError:
            raise ValueError(
                "Tên cột ly giác phải là số (mils)"
            )

        # Ma trận hiệu chỉnh (N x M)
        correction_matrix = df.iloc[:, 1:].to_numpy(dtype=float)

        return SlopeCorrectionService(
            slope_angles=slope_angles,
            elevation_mils=elevation_mils,
            correction_matrix=correction_matrix,
        )