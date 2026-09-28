import pandas as pd
import numpy as np

class DemandFeatureExtractor:
    """Extracts leak-free demand lag, rolling, trend, and momentum features."""

    def __init__(self, lags=[1, 2, 3, 7, 14, 28], rolling_windows=[3, 7, 14, 28], rolling_std_windows=[7, 14], ewm_alpha=0.3):
        self.lags = lags
        self.rolling_windows = rolling_windows
        self.rolling_std_windows = rolling_std_windows
        self.ewm_alpha = ewm_alpha

    def extract(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df.sort_values(["phc_id", "medicine_id", "date"]).reset_index(drop=True)
        grouped = df.groupby(["phc_id", "medicine_id"])

        # Target variable column to use for lags (observed demand / consumption)
        target_col = "observed_demand" if "observed_demand" in df.columns else "consumed_units"

        # 1. Lag features (strictly shifted by 1 or more timesteps)
        for lag in self.lags:
            df[f"demand_lag_{lag}"] = grouped[target_col].shift(lag)

        # 2. Rolling mean features (shift(1) ensures no target leakage)
        for w in self.rolling_windows:
            df[f"demand_rolling_mean_{w}"] = grouped[target_col].transform(lambda s: s.shift(1).rolling(w, min_periods=1).mean())

        # 3. Rolling std features
        for w in self.rolling_std_windows:
            df[f"demand_rolling_std_{w}"] = grouped[target_col].transform(lambda s: s.shift(1).rolling(w, min_periods=1).std()).fillna(0)

        # 4. EWM feature
        df["demand_ewm"] = grouped[target_col].transform(lambda s: s.shift(1).ewm(alpha=self.ewm_alpha, min_periods=1).mean())

        # 5. Momentum: ratio of 3-day rolling mean to 28-day rolling mean
        df["demand_momentum"] = (df["demand_rolling_mean_3"] + 1e-5) / (df["demand_rolling_mean_28"] + 1e-5)

        # 6. 7-day slope (trend approximation)
        df["demand_slope_7"] = (df["demand_lag_1"] - df["demand_lag_7"]) / 7.0

        # 7. Same-weekday historical demand (mean of same weekday over last 4 weeks: lag 7, 14, 21, 28)
        same_dow_sum = df["demand_lag_7"].fillna(0) + df["demand_lag_14"].fillna(0) + grouped[target_col].shift(21).fillna(0) + df["demand_lag_28"].fillna(0)
        df["same_weekday_mean_4w"] = same_dow_sum / 4.0

        return df
