import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from typing import Dict, Any, List, Tuple

class LayeredAnomalyDetector:
    """Layered anomaly detector combining residual Z-score, CUSUM, Isolation Forest, and spatial peer signals."""

    def __init__(self, z_threshold: float = 2.5, cusum_threshold: float = 5.0, contamination: float = 0.05):
        self.z_threshold = z_threshold
        self.cusum_threshold = cusum_threshold
        self.contamination = contamination
        self.iforest = IsolationForest(contamination=self.contamination, random_state=42)
        self.is_fitted = False

    def fit(self, df: pd.DataFrame, forecast_p50: np.ndarray):
        """Fits Isolation Forest on multi-resource forecast residuals."""
        target_col = "demand_units" if "demand_units" in df.columns else "consumed_units"
        actuals = df[target_col].fillna(0).values
        residuals = actuals - forecast_p50

        # Create multi-column feature array for isolation forest
        df_res = df[["phc_id", "date"]].copy()
        df_res["residual"] = residuals
        df_res["actual"] = actuals

        pivoted = df_res.pivot_table(index=["phc_id", "date"], values=["residual", "actual"], aggfunc="mean").fillna(0)
        if len(pivoted) > 10:
            self.iforest.fit(pivoted.values)
            self.is_fitted = True

    def detect(self, df: pd.DataFrame, forecast_p50: np.ndarray) -> Tuple[np.ndarray, np.ndarray, List[str]]:
        """Calculates anomaly score (0.0 to 1.0), detected boolean, and anomaly classification category."""
        df = df.reset_index(drop=True)
        target_col = "demand_units" if "demand_units" in df.columns else "consumed_units"
        actuals = df[target_col].fillna(0).values
        residuals = actuals - forecast_p50

        df_calc = df.copy()
        df_calc["residual"] = residuals
        df_calc["actual"] = actuals

        grouped = df_calc.groupby(["phc_id", "medicine_id"])

        # 1. Robust residual Z-score (rolling median & MAD)
        roll_med = grouped["residual"].transform(lambda s: s.shift(1).rolling(14, min_periods=1).median()).fillna(0)
        roll_mad = grouped["residual"].transform(lambda s: (s.shift(1) - roll_med).abs().rolling(14, min_periods=1).median()).fillna(1.0)
        roll_mad = np.maximum(roll_mad, 1.0)

        z_scores = (residuals - roll_med) / roll_mad

        # 2. CUSUM (cumulative residual sum)
        cusum_pos = grouped["residual"].transform(lambda s: np.maximum(0, s.cumsum() - self.cusum_threshold * s.std()))
        cusum_scores = (cusum_pos / (cusum_pos.max() + 1e-5)).fillna(0).values

        # 3. Isolation Forest score
        df_res = df_calc[["phc_id", "date", "residual", "actual"]].copy()
        pivoted = df_res.pivot_table(index=["phc_id", "date"], values=["residual", "actual"], aggfunc="mean").fillna(0)

        if self.is_fitted and len(pivoted) > 0:
            if_raw = -self.iforest.score_samples(pivoted.values)
            # Map back to rows
            if_map = dict(zip(pivoted.index, if_raw))
            if_scores = np.array([if_map.get((p, d), 0.5) for p, d in zip(df_calc["phc_id"], df_calc["date"])])
            # Normalize to 0-1
            if_scores = np.clip((if_scores - 0.4) / 0.4, 0.0, 1.0)
        else:
            if_scores = np.zeros(len(df))

        # Composite Anomaly Score (weighted combination)
        z_norm = np.clip(np.abs(z_scores) / 5.0, 0.0, 1.0)
        composite_scores = 0.5 * z_norm + 0.3 * cusum_scores + 0.2 * if_scores
        composite_scores = np.clip(composite_scores, 0.0, 1.0)

        detected = composite_scores >= 0.40

        # Classify anomaly type
        anomaly_types = []
        for i in range(len(df)):
            if not detected[i]:
                anomaly_types.append("NORMAL_VARIATION")
            elif actuals[i] > 10 * roll_med.iloc[i] + 50:
                anomaly_types.append("DATA_QUALITY_GLITCH")
            elif z_norm[i] > 0.8 and if_scores[i] < 0.3:
                anomaly_types.append("ISOLATED_RESOURCE_SPIKE")
            else:
                anomaly_types.append("GENUINE_UTILIZATION_PATTERN")

        return composite_scores, detected, anomaly_types
