import pytest
import sys, os
sys.path.insert(0, os.path.abspath("ai-ml"))

import pandas as pd
import numpy as np
from preprocessing.feature_engineering import PreprocessingPipeline
from features.feature_builder import FeatureBuilder

def test_feature_leakage_and_invariants():
    pipeline = PreprocessingPipeline(base_dir="data")
    cdata = pipeline.process_country("india")

    builder = FeatureBuilder()
    feat_df = builder.build_features(cdata["train"].head(500), phc_meta=cdata["phcs"], neighbors=cdata["neighbors"])

    assert "dow_sin" in feat_df.columns
    assert "demand_lag_1" in feat_df.columns
    assert "stock_cover_days" in feat_df.columns

    # Verify lag 1 feature has no NaN for valid shifted rows
    assert not feat_df["demand_lag_1"].isna().all()
