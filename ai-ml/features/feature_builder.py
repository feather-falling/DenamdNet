import pandas as pd
from typing import Dict, Any, List
from .temporal_features import TemporalFeatureExtractor
from .demand_features import DemandFeatureExtractor
from .inventory_features import InventoryFeatureExtractor
from .operational_features import OperationalFeatureExtractor
from .spatial_features import SpatialFeatureExtractor
from .resource_pattern_features import ResourcePatternFeatureExtractor

class FeatureBuilder:
    """Master feature builder that executes all feature extractors sequentially."""

    def __init__(self):
        self.temporal_extractor = TemporalFeatureExtractor()
        self.demand_extractor = DemandFeatureExtractor()
        self.inventory_extractor = InventoryFeatureExtractor()
        self.operational_extractor = OperationalFeatureExtractor()
        self.spatial_extractor = SpatialFeatureExtractor()
        self.pattern_extractor = ResourcePatternFeatureExtractor()

    def build_features(self, df: pd.DataFrame, staff_df: pd.DataFrame = None, phc_meta: List[Dict[str, Any]] = [], neighbors: Dict[str, Any] = {}) -> pd.DataFrame:
        """Extracts complete feature matrix for training/inference.
        Ensures strict temporal ordering and zero future lookahead.
        """
        df = self.temporal_extractor.extract(df)
        df = self.demand_extractor.extract(df)
        df = self.inventory_extractor.extract(df)
        df = self.operational_extractor.extract(df, staff_df)
        if phc_meta:
            df = self.spatial_extractor.extract(df, phc_meta, neighbors)
        df = self.pattern_extractor.extract(df)

        return df
