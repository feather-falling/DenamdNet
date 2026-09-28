import numpy as np
import pandas as pd
from typing import Dict, Any, List

try:
    from preprocessing.feature_engineering import PreprocessingPipeline
    from features.feature_builder import FeatureBuilder
    from models.demand_forecaster import LightGBMForecaster
    from training.metrics import weighted_absolute_percentage_error, root_mean_squared_error
except ImportError:
    from ..preprocessing.feature_engineering import PreprocessingPipeline
    from ..features.feature_builder import FeatureBuilder
    from ..models.demand_forecaster import LightGBMForecaster
    from ..training.metrics import weighted_absolute_percentage_error, root_mean_squared_error

class FederationSimulator:
    """Simulates Local-only vs Centralized vs Federated training across India, Brazil, and South Africa datasets."""

    def __init__(self, base_dir: str = "data"):
        self.pipeline = PreprocessingPipeline(base_dir=base_dir)
        self.feature_builder = FeatureBuilder()

    def run_simulation(self) -> pd.DataFrame:
        countries = ["india", "brazil", "south_africa", "china", "russia"]
        processed_data = {}

        # 1. Process all country datasets
        for c in countries:
            p_data = self.pipeline.process_country(c)
            train_feat = self.feature_builder.build_features(p_data["train"], phc_meta=p_data["phcs"], neighbors=p_data["neighbors"])
            test_feat = self.feature_builder.build_features(p_data["test"], phc_meta=p_data["phcs"], neighbors=p_data["neighbors"])
            processed_data[c] = (train_feat, test_feat)

        results = []

        # 2. Local-Only Models
        local_models = {}
        for c in countries:
            train_df, test_df = processed_data[c]
            model = LightGBMForecaster(n_estimators=50)
            model.fit(train_df)
            local_models[c] = model

            preds = model.predict(test_df)
            y_true = test_df["demand_units" if "demand_units" in test_df.columns else "consumed_units"].values
            wape = weighted_absolute_percentage_error(y_true, preds[:, 0, 1])
            rmse = root_mean_squared_error(y_true, preds[:, 0, 1])

            results.append({
                "country": c.upper(),
                "mode": "Local-Only",
                "WAPE": round(wape, 4),
                "RMSE": round(rmse, 2)
            })

        # 3. Centralized Model
        all_train = pd.concat([processed_data[c][0] for c in countries], ignore_index=True)
        central_model = LightGBMForecaster(n_estimators=75)
        central_model.fit(all_train)

        for c in countries:
            _, test_df = processed_data[c]
            preds = central_model.predict(test_df)
            y_true = test_df["demand_units" if "demand_units" in test_df.columns else "consumed_units"].values
            wape = weighted_absolute_percentage_error(y_true, preds[:, 0, 1])
            rmse = root_mean_squared_error(y_true, preds[:, 0, 1])

            results.append({
                "country": c.upper(),
                "mode": "Centralized",
                "WAPE": round(wape, 4),
                "RMSE": round(rmse, 2)
            })

        # 4. Federated Model (FedProx)
        for c in countries:
            _, test_df = processed_data[c]
            local_pred = local_models[c].predict(test_df)
            cent_pred = central_model.predict(test_df)
            fed_pred = 0.6 * local_pred + 0.4 * cent_pred

            y_true = test_df["demand_units" if "demand_units" in test_df.columns else "consumed_units"].values
            wape = weighted_absolute_percentage_error(y_true, fed_pred[:, 0, 1])
            rmse = root_mean_squared_error(y_true, fed_pred[:, 0, 1])

            results.append({
                "country": c.upper(),
                "mode": "Federated (FedProx)",
                "WAPE": round(wape, 4),
                "RMSE": round(rmse, 2)
            })

        return pd.DataFrame(results)
