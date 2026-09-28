import pandas as pd
import numpy as np

class OperationalFeatureExtractor:
    """Extracts leak-free operational features: OPD visits, staff availability, diagnostic usage."""

    def extract(self, df: pd.DataFrame, staff_df: pd.DataFrame = None) -> pd.DataFrame:
        df = df.copy()
        df = df.sort_values(["phc_id", "medicine_id", "date"]).reset_index(drop=True)
        grouped = df.groupby(["phc_id", "medicine_id"])

        # Patient visits (footfall lag 1 & rolling 7)
        if "patient_visits" in df.columns:
            df["footfall_lag_1"] = grouped["patient_visits"].shift(1)
            df["footfall_rolling_7"] = grouped["patient_visits"].transform(lambda s: s.shift(1).rolling(7, min_periods=1).mean())
            df["consumption_per_visit"] = (df["demand_lag_1"] if "demand_lag_1" in df.columns else grouped["consumed_units"].shift(1)) / (df["footfall_lag_1"] + 1.0)
        else:
            df["footfall_lag_1"] = 0
            df["footfall_rolling_7"] = 0
            df["consumption_per_visit"] = 0

        # Diagnostic usage per visit
        if "diagnostic_usage_units" in df.columns and "patient_visits" in df.columns:
            df["diag_usage_lag_1"] = grouped["diagnostic_usage_units"].shift(1)
            df["diag_per_visit"] = df["diag_usage_lag_1"] / (df["footfall_lag_1"] + 1.0)
        else:
            df["diag_usage_lag_1"] = 0
            df["diag_per_visit"] = 0

        # Merge staff attendance features if provided
        if staff_df is not None and not staff_df.empty:
            staff_clean = staff_df.groupby(["phc_id", "date"])["absence_rate"].mean().reset_index()
            staff_clean["date"] = pd.to_datetime(staff_clean["date"])
            df = pd.merge(df, staff_clean, on=["phc_id", "date"], how="left")
            df["absence_rate"] = df.groupby(["phc_id", "medicine_id"])["absence_rate"].transform(lambda s: s.shift(1).fillna(0))
        else:
            df["absence_rate"] = 0.0

        return df
