import os
import sys
import json
import jsonschema
import pytest
import pandas as pd
import numpy as np

# Ensure ai-ml is on sys.path
sys.path.insert(0, os.path.abspath("ai-ml"))

from run_daily_prediction import (
    normalize_country_name,
    append_or_update_csv,
    ingest_daily_input,
    run_daily_prediction_pipeline
)

def test_normalize_country_name():
    assert normalize_country_name("India") == "india"
    assert normalize_country_name("IN") == "india"
    assert normalize_country_name("Brazil") == "brazil"
    assert normalize_country_name("Brasil") == "brazil"
    assert normalize_country_name("BR") == "brazil"
    assert normalize_country_name("South Africa") == "south_africa"
    assert normalize_country_name("south_africa") == "south_africa"
    assert normalize_country_name("ZA") == "south_africa"
    assert normalize_country_name("China") == "china"
    assert normalize_country_name("china") == "china"
    assert normalize_country_name("CN") == "china"
    assert normalize_country_name("Russia") == "russia"
    assert normalize_country_name("russia") == "russia"
    assert normalize_country_name("RU") == "russia"


def test_append_or_update_csv(tmp_path):
    test_csv = tmp_path / "test_inventory.csv"
    
    # Create initial CSV
    df1 = pd.DataFrame([
        {"date": "2026-09-18", "phc_id": "PHC-1", "medicine_id": "MED-1", "closing_stock": 100},
        {"date": "2026-09-18", "phc_id": "PHC-2", "medicine_id": "MED-1", "closing_stock": 200},
    ])
    df1.to_csv(test_csv, index=False)

    # Update PHC-1 and add PHC-3
    df2 = pd.DataFrame([
        {"date": "2026-09-18", "phc_id": "PHC-1", "medicine_id": "MED-1", "closing_stock": 150},
        {"date": "2026-09-18", "phc_id": "PHC-3", "medicine_id": "MED-1", "closing_stock": 300},
    ])
    append_or_update_csv(str(test_csv), df2, key_cols=["date", "phc_id", "medicine_id"])

    res = pd.read_csv(test_csv)
    assert len(res) == 3
    # Verify PHC-1 was updated, not duplicated
    phc1 = res[(res["phc_id"] == "PHC-1") & (res["date"] == "2026-09-18")]
    assert len(phc1) == 1
    assert phc1.iloc[0]["closing_stock"] == 150
    # Verify PHC-3 was added
    phc3 = res[res["phc_id"] == "PHC-3"]
    assert len(phc3) == 1
    assert phc3.iloc[0]["closing_stock"] == 300


def test_daily_prediction_pipeline_dry_run(tmp_path):
    # Test pipeline with dry_run to ensure end-to-end inference and JSON contract generation
    test_input = tmp_path / "sample_input.json"
    pred_output = tmp_path / "predictions.json"
    alert_output = tmp_path / "alerts.json"

    input_payload = {
      "country": "india",
      "date": "2026-09-18",
      "records": [
        {
          "phc_id": "IN-UP-MEE-001",
          "medicine_id": "MED-001",
          "opening_stock": 600,
          "received_units": 0,
          "consumed_units": 45,
          "closing_stock": 555,
          "demand_units": 45,
          "patient_visits": 310,
          "diagnostic_usage_units": 15
        }
      ]
    }
    with open(test_input, "w") as f:
        json.dump(input_payload, f)

    result = run_daily_prediction_pipeline(
        input_file=str(test_input),
        output_predictions_path=str(pred_output),
        output_alerts_path=str(alert_output),
        base_dir="data",
        dry_run=True
    )

    # Check files created
    assert os.path.exists(pred_output)
    assert os.path.exists(alert_output)

    # Validate against prediction schema
    schema_path = os.path.join("ai-ml", "schemas", "prediction_schema.json")
    with open(schema_path, "r") as f:
        schema = json.load(f)

    with open(pred_output, "r") as f:
        predictions = json.load(f)

    assert len(predictions) >= 1
    for rec in predictions:
        jsonschema.validate(instance=rec, schema=schema)
        assert "timestamp" in rec
        assert "phc_id" in rec
        assert "country_code" in rec
        assert "forecast_demand" in rec
        assert "stockout" in rec
        assert "risk" in rec
        assert "anomaly" in rec
        assert "inventory_protection" in rec
