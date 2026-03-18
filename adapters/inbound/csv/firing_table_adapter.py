import pandas as pd
from domain.services.targeting_system import FiringTableInterpolator


def load_firing_table(csv_path: str) -> FiringTableInterpolator:
    df = pd.read_csv(csv_path)

    ranges = df["X"].values
    angles = df["P"].values

    extra = {
        col: df[col].values
        for col in df.columns
        if col not in ("X", "P")
    }

    return FiringTableInterpolator(
        ranges=ranges,
        angle_mils=angles,
        extra_fields=extra,
    )
