import numpy as np
import pandas as pd
from typing import Dict, Any

try:
    from training.metrics import (
        mean_absolute_error, root_mean_squared_error, 
        weighted_absolute_percentage_error, forecast_bias, quantile_coverage
    )
    from models.baselines import SeasonalNaiveBaseline, MovingAverageBaseline
    from models.demand_forecaster import LightGBMForecaster, DemandNetForecaster
except ImportError:
    from .metrics import (
        mean_absolute_error, root_mean_squared_error, 
        weighted_absolute_percentage_error, forecast_bias, quantile_coverage
    )
    from models.baselines import SeasonalNaiveBaseline, MovingAverageBaseline
    from ..models.demand_forecaster import LightGBMForecaster, DemandNetForecaster

class RollingOriginBacktester:
    """Evaluates forecasters using rolling-origin backtesting without leakage."""

    def __init__(self, horizon: int = 7):
        self.horizon = horizon

    def evaluate_model(self, model: Any, train_df: pd.DataFrame, test_df: pd.DataFrame, model_name: str) -> Dict[str, float]:
        target_col = "demand_units" if "demand_units" in test_df.columns else "consumed_units"
        
        # Fit model on training set
        if hasattr(model, "fit"):
            model.fit(train_df, target_col=target_col)

        # Predict on test set
        preds = model.predict(test_df) # (N, 7, 3)

        y_true = test_df[target_col].fillna(0).values
        p10 = preds[:, 0, 0]
        p50 = preds[:, 0, 1] # Horizon 1 prediction for metric summary
        p90 = preds[:, 0, 2]

        mae = mean_absolute_error(y_true, p50)
        rmse = root_mean_squared_error(y_true, p50)
        wape = weighted_absolute_percentage_error(y_true, p50)
        bias = forecast_bias(y_true, p50)
        cov = quantile_coverage(y_true, p10, p90)

        return {
            "model": model_name,
            "MAE": round(mae, 2),
            "RMSE": round(rmse, 2),
            "WAPE": round(wape, 4),
            "Bias": round(bias, 4),
            "QuantileCoverage_P10_P90": round(cov, 4)
        }

    def run_comparison(self, train_df: pd.DataFrame, test_df: pd.DataFrame) -> pd.DataFrame:
        results = []

        # 1. Seasonal Naive
        sn = SeasonalNaiveBaseline()
        results.append(self.evaluate_model(sn, train_df, test_df, "Seasonal Naive"))

        # 2. Moving Average
        ma = MovingAverageBaseline()
        results.append(self.evaluate_model(ma, train_df, test_df, "Moving Average (7d)"))

        # 3. LightGBM
        lgb_model = LightGBMForecaster(n_estimators=100)
        results.append(self.evaluate_model(lgb_model, train_df, test_df, "LightGBM Quantile"))

        # 4. DemandNet
        dnet = DemandNetForecaster(epochs=5, batch_size=128)
        results.append(self.evaluate_model(dnet, train_df, test_df, "DemandNet (GRU+Tabular)"))

        return pd.DataFrame(results)
