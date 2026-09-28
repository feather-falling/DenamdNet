import pandas as pd
import numpy as np

class InventoryFeatureExtractor:
    """Extracts leak-free inventory features: stock cover, censoring indicators, stockout flags."""

    def extract(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df = df.sort_values(["phc_id", "medicine_id", "date"]).reset_index(drop=True)
        grouped = df.groupby(["phc_id", "medicine_id"])

        # Lagged closing stock (shift 1)
        df["closing_stock_lag_1"] = grouped["closing_stock"].shift(1)

        # 7-day rolling mean demand
        demand_s = grouped["consumed_units"].transform(lambda s: s.shift(1).rolling(7, min_periods=1).mean()).fillna(1.0)
        df["demand_rolling_mean_7"] = demand_s

        # Stock cover days = lagged stock / 7-day rolling demand
        df["stock_cover_days"] = (df["closing_stock_lag_1"] + 1e-5) / (df["demand_rolling_mean_7"] + 1e-5)

        # Stockout lag (whether closing stock at t-1 was 0)
        df["stockout_lag_1"] = (df["closing_stock_lag_1"] <= 0).astype(int)

        # Censored fraction in last 14 days
        censored_col = "is_censored" if "is_censored" in df.columns else (df["closing_stock"] <= 0).astype(int)
        df["censored_fraction_14d"] = grouped[censored_col].transform(lambda s: s.shift(1).rolling(14, min_periods=1).mean()).fillna(0)

        return df
