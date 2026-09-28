import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

class SeasonalNaiveBaseline:
    """Seasonal Naive Baseline: Predicts t+h using demand from t+h-7."""

    def predict(self, df: pd.DataFrame, horizon: int = 7) -> np.ndarray:
        """Returns predictions of shape (N, horizon, 3) for P10, P50, P90."""
        # Use lag 7 demand as P50 forecast
        p50 = df["demand_lag_7"].fillna(0).values if "demand_lag_7" in df.columns else df["consumed_units"].values
        p50 = np.clip(p50, 0, None)

        N = len(df)
        preds = np.zeros((N, horizon, 3))
        for h in range(horizon):
            preds[:, h, 0] = p50 * 0.7  # P10
            preds[:, h, 1] = p50        # P50
            preds[:, h, 2] = p50 * 1.4  # P90
        return preds

class MovingAverageBaseline:
    """7-Day Moving Average Baseline."""

    def predict(self, df: pd.DataFrame, horizon: int = 7) -> np.ndarray:
        """Returns predictions of shape (N, horizon, 3) for P10, P50, P90."""
        p50 = df["demand_rolling_mean_7"].fillna(0).values if "demand_rolling_mean_7" in df.columns else df["consumed_units"].values
        p50 = np.clip(p50, 0, None)

        N = len(df)
        preds = np.zeros((N, horizon, 3))
        for h in range(horizon):
            preds[:, h, 0] = p50 * 0.75 # P10
            preds[:, h, 1] = p50        # P50
            preds[:, h, 2] = p50 * 1.35 # P90
        return preds
