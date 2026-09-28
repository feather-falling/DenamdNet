import pytest
import sys, os
sys.path.insert(0, os.path.abspath("ai-ml"))

import json
import jsonschema
import numpy as np
import pandas as pd
from inference.prediction_service import PredictionService

def test_sharma_exact_json_contract():
    service = PredictionService()
    
    df = pd.DataFrame([{
        "date": "2026-09-18",
        "phc_id": "IN-UP-MEE-001",
        "medicine_id": "MED-001",
        "closing_stock": 600,
        "opening_stock": 600
    }])

    q_preds = np.array([[[100, 120, 150]] * 7])
    anom_scores = np.array([0.15])
    anom_detected = np.array([False])

    med_cat = [{"medicine_id": "MED-001", "name": "Paracetamol", "unit": "tablet", "category": "ESSENTIAL"}]
    phc_cat = [{"phc_id": "IN-UP-MEE-001", "country": "India", "state": "Uttar Pradesh", "district": "Meerut"}]

    records = service.generate_sharma_records(df, q_preds, anom_scores, anom_detected, med_cat, phc_cat)
    assert len(records) == 1
    rec = records[0]

    # Validate against JSON schema
    schema_path = os.path.join("ai-ml", "schemas", "prediction_schema.json")
    with open(schema_path, "r") as f:
        schema = json.load(f)

    jsonschema.validate(instance=rec, schema=schema)
    assert rec["phc_id"] == "IN-UP-MEE-001"
    assert rec["country_code"] == "IN"
    assert "forecast_demand" in rec
    assert "stockout" in rec
    assert "risk" in rec
    assert "inventory_protection" in rec
