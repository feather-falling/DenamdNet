import pandas as pd

class DataCleaner:
    """Cleans raw data: converts dates to datetime, sorts, deduplicates."""

    def clean_demand(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["phc_id", "medicine_id", "date"]).reset_index(drop=True)
        # Deduplicate keeping last
        df = df.drop_duplicates(subset=["phc_id", "medicine_id", "date"], keep="last")
        return df

    def clean_inventory(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["phc_id", "medicine_id", "date"]).reset_index(drop=True)
        df = df.drop_duplicates(subset=["phc_id", "medicine_id", "date"], keep="last")
        return df

    def clean_staff(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values(["phc_id", "staff_category", "date"]).reset_index(drop=True)
        df = df.drop_duplicates(subset=["phc_id", "staff_category", "date"], keep="last")
        return df
