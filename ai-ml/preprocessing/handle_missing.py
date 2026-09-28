import pandas as pd
import numpy as np

class MissingDataHandler:
    """Ensures complete calendar grid per (phc_id, medicine_id) and interpolates short gaps."""

    def reindex_and_interpolate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Reindexes dataset to full daily calendar grid per PHC/medicine series."""
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        
        phcs = df["phc_id"].unique()
        meds = df["medicine_id"].unique()
        min_date = df["date"].min()
        max_date = df["date"].max()

        full_dates = pd.date_range(min_date, max_date, freq="D")
        full_index = pd.MultiIndex.from_product([phcs, meds, full_dates], names=["phc_id", "medicine_id", "date"])

        indexed_df = df.set_index(["phc_id", "medicine_id", "date"]).reindex(full_index).reset_index()

        # Mark missing gaps
        indexed_df["was_missing"] = indexed_df["demand_units"].isna().astype(int)

        # Forward fill inventory opening stock if missing, interpolate demand for short gaps (<= 2 days)
        numeric_cols = ["demand_units", "patient_visits", "diagnostic_usage_units", "consumed_units", "closing_stock"]
        for col in numeric_cols:
            if col in indexed_df.columns:
                indexed_df[col] = indexed_df.groupby(["phc_id", "medicine_id"])[col].transform(
                    lambda s: s.interpolate(method="linear", limit=2).ffill().bfill().fillna(0)
                )

        return indexed_df
