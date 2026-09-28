import pandas as pd
import numpy as np

class TemporalFeatureExtractor:
    """Extracts leak-free calendar, seasonal, and holiday features."""

    def extract(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        dt = pd.to_datetime(df["date"])

        # Calendar units
        day_of_week = dt.dt.dayofweek
        month = dt.dt.month
        day_of_year = dt.dt.dayofyear

        # Cyclical sin/cos encodings
        df["dow_sin"] = np.sin(2 * np.pi * day_of_week / 7.0)
        df["dow_cos"] = np.cos(2 * np.pi * day_of_week / 7.0)
        df["month_sin"] = np.sin(2 * np.pi * month / 12.0)
        df["month_cos"] = np.cos(2 * np.pi * month / 12.0)
        df["doy_sin"] = np.sin(2 * np.pi * day_of_year / 365.25)
        df["doy_cos"] = np.cos(2 * np.pi * day_of_year / 365.25)

        # Weekend indicator
        df["is_weekend"] = (day_of_week >= 5).astype(int)

        return df
