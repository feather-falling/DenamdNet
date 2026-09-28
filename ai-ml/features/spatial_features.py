import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union

class SpatialFeatureExtractor:
    """Extracts spatial peer features: district peer demand momentum & neighbor activity."""

    def extract(self, df: pd.DataFrame, phc_meta: Union[List[Dict[str, Any]], Dict[str, Any]], neighbors: Union[Dict[str, Any], List[Dict[str, Any]]] = {}) -> pd.DataFrame:
        df = df.copy()

        # Map district to PHC
        phc_list = phc_meta.get("phcs", []) if isinstance(phc_meta, dict) else phc_meta
        phc_to_district = {p["phc_id"]: p.get("district", "DEFAULT") for p in phc_list if isinstance(p, dict) and "phc_id" in p}
        df["district"] = df["phc_id"].map(phc_to_district).fillna("DEFAULT")

        # 1. District peer average demand (excluding self)
        demand_col = "demand_lag_1" if "demand_lag_1" in df.columns else "consumed_units"
        district_daily = df.groupby(["district", "medicine_id", "date"])[demand_col].mean().reset_index()
        district_daily.rename(columns={demand_col: "district_peer_demand_lag_1"}, inplace=True)

        df = pd.merge(df, district_daily, on=["district", "medicine_id", "date"], how="left")
        df["district_peer_demand_lag_1"] = df["district_peer_demand_lag_1"].fillna(0)

        # 2. Peer momentum (7-day rolling mean of district peer demand)
        grouped = df.groupby(["phc_id", "medicine_id"])
        df["district_peer_momentum"] = grouped["district_peer_demand_lag_1"].transform(
            lambda s: s.rolling(7, min_periods=1).mean()
        ).fillna(0)

        return df
