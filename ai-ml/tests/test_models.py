import pytest
import sys, os
sys.path.insert(0, os.path.abspath("ai-ml"))

import pandas as pd
import numpy as np
from models.baselines import SeasonalNaiveBaseline, MovingAverageBaseline
from models.demand_forecaster import LightGBMForecaster
from models.anomaly_detector import LayeredAnomalyDetector
from models.pattern_detector import MultiResourcePatternDetector

def test_forecasting_models_output_shape():
    df = pd.DataFrame({
        "date": pd.date_range("2025-10-01", periods=50),
        "phc_id": "IN-UP-MEE-001",
        "medicine_id": "MED-001",
        "consumed_units": np.random.randint(10, 50, size=50),
        "demand_units": np.random.randint(10, 50, size=50),
        "demand_lag_1": np.random.randint(10, 50, size=50),
        "demand_lag_7": np.random.randint(10, 50, size=50),
        "demand_rolling_mean_7": np.random.randint(10, 50, size=50)
    })

    sn = SeasonalNaiveBaseline()
    sn_preds = sn.predict(df)
    assert sn_preds.shape == (50, 7, 3)

    ma = MovingAverageBaseline()
    ma_preds = ma.predict(df)
    assert ma_preds.shape == (50, 7, 3)

def test_anomaly_and_pattern_detectors():
    df = pd.DataFrame({
        "date": "2025-10-01",
        "phc_id": "IN-UP-MEE-001",
        "medicine_id": "MED-001",
        "consumed_units": 150,
        "demand_units": 150,
        "closing_stock": 10,
        "district": "Meerut",
        "country_code": "IN"
    }, index=[0])

    p50 = np.array([20.0])
    detector = LayeredAnomalyDetector()
    scores, detected, types = detector.detect(df, p50)
    assert len(scores) == 1
    assert len(detected) == 1
    assert types[0] in ["NORMAL_VARIATION", "DATA_QUALITY_GLITCH", "ISOLATED_RESOURCE_SPIKE", "GENUINE_UTILIZATION_PATTERN"]
