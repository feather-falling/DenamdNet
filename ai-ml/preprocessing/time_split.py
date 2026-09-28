import pandas as pd
import numpy as np
from typing import Dict, Tuple, List

class TimeSplitter:
    """Performs strict chronological time splitting and cold-start PHC splits."""

    def __init__(self, val_days: int = 28, test_days: int = 56, purge_days: int = 7, cold_start_ratio: float = 0.1):
        self.val_days = val_days
        self.test_days = test_days
        self.purge_days = purge_days
        self.cold_start_ratio = cold_start_ratio

    def temporal_split(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Splits DataFrame chronologically into train, validation, and test sets.
        Prevents target leakage by purging purge_days between splits.
        """
        df = df.copy()
        df["date"] = pd.to_datetime(df["date"])
        max_date = df["date"].max()

        test_start = max_date - pd.Timedelta(days=self.test_days - 1)
        val_end = test_start - pd.Timedelta(days=self.purge_days)
        val_start = val_end - pd.Timedelta(days=self.val_days - 1)
        train_end = val_start - pd.Timedelta(days=self.purge_days)

        train_df = df[df["date"] <= train_end].copy()
        val_df = df[(df["date"] >= val_start) & (df["date"] <= val_end)].copy()
        test_df = df[df["date"] >= test_start].copy()

        return train_df, val_df, test_df

    def cold_start_split(self, df: pd.DataFrame, seed: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, List[str]]:
        """Splits PHCs into seen training PHCs and unseen cold-start holdout PHCs."""
        phcs = np.sort(df["phc_id"].unique())
        np.random.seed(seed)
        n_cold = int(len(phcs) * self.cold_start_ratio)
        cold_phcs = set(np.random.choice(phcs, size=n_cold, replace=False))

        seen_df = df[~df["phc_id"].isin(cold_phcs)].copy()
        cold_df = df[df["phc_id"].isin(cold_phcs)].copy()

        return seen_df, cold_df, list(cold_phcs)
