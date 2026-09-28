import pandas as pd
import numpy as np

class ResourcePatternFeatureExtractor:
    """Extracts multi-resource co-movement and correlation features across items at each PHC."""

    def extract(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Pivot to get daily lag_1 demand for all medicines at each (phc_id, date)
        demand_col = "demand_lag_1" if "demand_lag_1" in df.columns else "consumed_units"
        pivoted = df.pivot_table(
            index=["phc_id", "date"], 
            columns="medicine_id", 
            values=demand_col, 
            fill_value=0
        )

        # Compute facility total demand & max category spike ratio
        facility_total = pivoted.sum(axis=1).rename("phc_total_demand_lag_1")
        facility_max = pivoted.max(axis=1).rename("phc_max_resource_lag_1")
        facility_breadth = (pivoted > 0).sum(axis=1).rename("phc_active_resource_count")

        pivoted_features = pd.concat([facility_total, facility_max, facility_breadth], axis=1).reset_index()

        df = pd.merge(df, pivoted_features, on=["phc_id", "date"], how="left")
        df["phc_total_demand_lag_1"] = df["phc_total_demand_lag_1"].fillna(0)
        df["phc_max_resource_lag_1"] = df["phc_max_resource_lag_1"].fillna(0)
        df["phc_active_resource_count"] = df["phc_active_resource_count"].fillna(0)

        # Resource share of facility demand
        df["resource_share_of_phc_demand"] = (df[demand_col] + 1e-5) / (df["phc_total_demand_lag_1"] + 1e-5)

        return df
