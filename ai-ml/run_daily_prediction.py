import os
import sys
import json
import argparse
import pandas as pd
import numpy as np
from datetime import datetime, timezone
from typing import Dict, Any, List, Tuple

# Ensure ai-ml package directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from preprocessing.load_data import DataLoader
from preprocessing.feature_engineering import PreprocessingPipeline
from features.feature_builder import FeatureBuilder
from models.anomaly_detector import LayeredAnomalyDetector
from models.pattern_detector import MultiResourcePatternDetector
from models.demand_forecaster import LightGBMForecaster
from inference.prediction_service import PredictionService


def normalize_country_name(country: str) -> str:
    """Normalizes country string to matching dataset folder name."""
    c = country.strip().lower().replace(" ", "_").replace("-", "_")
    if c in ["india", "in"]:
        return "india"
    elif c in ["brazil", "br", "brasil"]:
        return "brazil"
    elif c in ["south_africa", "southafrica", "za", "sa"]:
        return "south_africa"
    elif c in ["china", "cn"]:
        return "china"
    elif c in ["russia", "ru", "russian_federation"]:
        return "russia"
    elif c in ["all", "global", "multi", "multicountry"]:
        return "all"
    return c


def append_or_update_csv(csv_path: str, new_rows_df: pd.DataFrame, key_cols: List[str]) -> int:
    """Appends new rows to an existing CSV, updating rows if (key_cols) already exist.
    Guarantees idempotency and prevents duplicate entries.
    """
    if os.path.exists(csv_path):
        existing_df = pd.read_csv(csv_path)
        
        # Format key columns as strings for reliable comparison
        existing_keys = set(existing_df[key_cols].astype(str).agg("_".join, axis=1))
        new_keys = set(new_rows_df[key_cols].astype(str).agg("_".join, axis=1))
        
        # Filter out existing rows that are being overwritten
        filtered_existing = existing_df[~existing_df[key_cols].astype(str).agg("_".join, axis=1).isin(new_keys)]
        
        # Combine filtered existing with new records
        combined_df = pd.concat([filtered_existing, new_rows_df], ignore_index=True)
        # Ensure column order is preserved from existing file
        combined_df = combined_df.reindex(columns=existing_df.columns)
    else:
        combined_df = new_rows_df

    combined_df.to_csv(csv_path, index=False)
    return len(new_rows_df)


def ingest_daily_input(input_data: Dict[str, Any], base_dir: str = "data") -> Tuple[str, str, int]:
    """Parses input JSON, routes data to appropriate country folder, and appends to CSVs.
    Returns (country, target_date, num_records_processed).
    """
    raw_country = input_data.get("country", "india")
    country = normalize_country_name(raw_country)
    country_dir = os.path.join(base_dir, country)
    
    if not os.path.exists(country_dir):
        raise FileNotFoundError(f"Country directory not found: {country_dir} for country '{raw_country}'")

    target_date = input_data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    records = input_data.get("records", [])
    staff_records = input_data.get("staff_attendance", [])

    def _phc_matches_country(pid: str, c: str) -> bool:
        if c == "india":
            return pid.startswith("IN-")
        elif c == "brazil":
            return pid.startswith("BR-")
        elif c == "south_africa":
            return pid.startswith("ZA-")
        elif c == "china":
            return pid.startswith("CN-")
        elif c == "russia":
            return pid.startswith("RU-")
        return True

    # Filter to records relevant to this country
    records = [r for r in records if _phc_matches_country(r.get("phc_id", ""), country)]
    staff_records = [s for s in staff_records if _phc_matches_country(s.get("phc_id", ""), country)]

    if not records:
        print(f"[WARN] No facility/medicine records found in daily input JSON for country '{country}'.")
        return country, target_date, 0

    # 1. Prepare inventory records
    inv_rows = []
    dem_rows = []

    for rec in records:
        phc_id = rec["phc_id"]
        medicine_id = rec["medicine_id"]
        rec_date = rec.get("date", target_date)
        
        opening_stock = float(rec.get("opening_stock", 0))
        received_units = float(rec.get("received_units", 0))
        consumed_units = float(rec.get("consumed_units", 0))
        out_transfer = float(rec.get("outgoing_transfer_units", 0))
        in_transfer = float(rec.get("incoming_transfer_units", 0))
        
        # Auto-calculate closing_stock if not provided
        if "closing_stock" in rec and rec["closing_stock"] is not None:
            closing_stock = float(rec["closing_stock"])
        else:
            closing_stock = max(0.0, opening_stock + received_units + in_transfer - consumed_units - out_transfer)

        # Demand & unmet demand
        demand_units = float(rec.get("demand_units", consumed_units))
        unmet_units = float(rec.get("unmet_demand_units", max(0.0, demand_units - consumed_units)))
        patient_visits = int(rec.get("patient_visits", 300))
        diagnostic_units = int(rec.get("diagnostic_usage_units", 20))
        provenance = rec.get("provenance", "INPUT_TELEMETRY")

        inv_rows.append({
            "date": rec_date,
            "phc_id": phc_id,
            "medicine_id": medicine_id,
            "opening_stock": opening_stock,
            "received_units": received_units,
            "consumed_units": consumed_units,
            "outgoing_transfer_units": out_transfer,
            "incoming_transfer_units": in_transfer,
            "closing_stock": closing_stock,
            "unmet_demand_units": unmet_units,
            "provenance": provenance
        })

        dem_rows.append({
            "date": rec_date,
            "phc_id": phc_id,
            "medicine_id": medicine_id,
            "demand_units": demand_units,
            "patient_visits": patient_visits,
            "diagnostic_usage_units": diagnostic_units,
            "provenance": provenance
        })

    # Ingest into inventory.csv
    inv_df = pd.DataFrame(inv_rows)
    inv_path = os.path.join(country_dir, "inventory.csv")
    append_or_update_csv(inv_path, inv_df, key_cols=["date", "phc_id", "medicine_id"])

    # Ingest into demand.csv
    dem_df = pd.DataFrame(dem_rows)
    dem_path = os.path.join(country_dir, "demand.csv")
    append_or_update_csv(dem_path, dem_df, key_cols=["date", "phc_id", "medicine_id"])

    # Ingest into staff_attendance.csv if present
    if staff_records:
        staff_rows = []
        for srec in staff_records:
            staff_rows.append({
                "date": srec.get("date", target_date),
                "phc_id": srec["phc_id"],
                "doctors_present": int(srec.get("doctors_present", 2)),
                "nurses_present": int(srec.get("nurses_present", 4)),
                "pharmacists_present": int(srec.get("pharmacists_present", 1)),
                "provenance": srec.get("provenance", "INPUT_TELEMETRY")
            })
        staff_df = pd.DataFrame(staff_rows)
        staff_path = os.path.join(country_dir, "staff_attendance.csv")
        append_or_update_csv(staff_path, staff_df, key_cols=["date", "phc_id"])

    return country, target_date, len(records)


def run_daily_prediction_pipeline(
    input_file: str,
    country_override: str = None,
    output_predictions_path: str = "outputs/predictions/predictions.json",
    output_alerts_path: str = "outputs/alerts/alerts.json",
    base_dir: str = "data",
    dry_run: bool = False
) -> Dict[str, Any]:
    """Executes the complete daily workflow:
    1. Reads daily input JSON.
    2. Appends data to respective country CSVs (if not dry_run).
    3. Generates features and ML forecasts.
    4. Detects stockouts, anomalies, and multi-resource outbreak patterns.
    5. Saves outputs to separate JSON files (Sharma contract & Alerts).
    """
    print("=" * 80)
    print("  BRICS HEALTH RESILIENCE ML SYSTEM -- DAILY OPERATIONAL INGESTION & INFERENCE")
    print("=" * 80)

    # 1. Load Input JSON
    if not os.path.exists(input_file):
        # Check alternative common paths
        alt_paths = [
            input_file,
            os.path.join("inputs", os.path.basename(input_file)),
            os.path.join("input", os.path.basename(input_file)),
            os.path.join("inputs", "input_today.json"),
            os.path.join("input", "input_today.json"),
            os.path.join("inputs", "daily_input_template.json"),
            os.path.join("input", "daily_input_template.json"),
            os.path.join("data", os.path.basename(input_file)),
            os.path.join("data", "daily_telemetry_input.json")
        ]
        found = False
        for alt in alt_paths:
            if os.path.exists(alt):
                input_file = alt
                found = True
                break
        if not found:
            raise FileNotFoundError(f"Input JSON file not found: {input_file}")

    print(f"Reading input file: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        input_data = json.load(f)

    if country_override:
        input_data["country"] = country_override

    # 2. Ingestion & Country Routing
    country = normalize_country_name(input_data.get("country", "india"))
    target_date = input_data.get("date", datetime.now(timezone.utc).strftime("%Y-%m-%d"))

    if country == "all":
        all_sharma = []
        all_alerts = []
        for c in ["india", "brazil", "south_africa", "china", "russia"]:
            sub_res = run_daily_prediction_pipeline(
                input_file=input_file,
                country_override=c,
                output_predictions_path=f"outputs/predictions/predictions_{c}.json",
                output_alerts_path=f"outputs/alerts/alerts_{c}.json",
                base_dir=base_dir,
                dry_run=dry_run
            )
            all_sharma.extend(sub_res.get("sharma_records", []))
            all_alerts.extend(sub_res.get("alerts", []))

        # Save combined output files
        target_pred_dirs = [output_predictions_path, "output/alerts/predictions.json", "outputs/predictions/predictions.json", "outputs/alerts/predictions.json"]
        for p_path in set(target_pred_dirs):
            os.makedirs(os.path.dirname(os.path.abspath(p_path)), exist_ok=True)
            with open(p_path, "w", encoding="utf-8") as f:
                json.dump(all_sharma, f, indent=2)

        target_alert_dirs = [output_alerts_path, "output/alerts/alerts.json", "outputs/alerts/alerts.json"]
        for a_path in set(target_alert_dirs):
            os.makedirs(os.path.dirname(os.path.abspath(a_path)), exist_ok=True)
            with open(a_path, "w", encoding="utf-8") as f:
                json.dump(all_alerts, f, indent=2)

        print(f"\n[SUCCESS] Multi-country daily pipeline completed across India, Brazil, South Africa, China, Russia.")
        print(f"Total Predictions: {len(all_sharma)} | Total Alerts: {len(all_alerts)}")
        print("=" * 80)

        return {
            "country": "all",
            "date": target_date,
            "sharma_records": all_sharma,
            "alerts": all_alerts,
            "output_predictions": output_predictions_path,
            "output_alerts": output_alerts_path
        }

    print(f"\n[Step 1] Processing Daily Input for Country: [{country.upper()}] (Target Date: {target_date})")
    
    if dry_run:
        print("   [DRY RUN] Skipping CSV file writes.")
        num_records = len(input_data.get("records", []))
    else:
        country, target_date, num_records = ingest_daily_input(input_data, base_dir=base_dir)
        print(f"   [OK] Appended/Updated {num_records} telemetry records in 'data/{country}/'.")

    # 3. Load & Preprocess Data for Feature Building
    print(f"\n[Step 2] Loading & Preprocessing Country Data...")
    loader = DataLoader(base_dir=base_dir)
    cdata = loader.load_country_data(country)
    
    pipeline = PreprocessingPipeline(base_dir=base_dir)
    processed_country = pipeline.process_country(country)
    full_grid = processed_country["full_grid"]

    # Filter to recent historical window (last 60 days) to optimize feature computation
    max_date = pd.to_datetime(target_date)
    min_date = max_date - pd.Timedelta(days=60)
    recent_grid = full_grid[pd.to_datetime(full_grid["date"]) >= min_date].copy()

    # If target date row wasn't in full_grid yet (e.g. fresh append), ensure it is processed
    if not any(recent_grid["date"] == target_date) and not dry_run:
        recent_grid = full_grid.copy()

    print(f"   [OK] Loaded grid with {len(recent_grid)} rows spanning {min_date.strftime('%Y-%m-%d')} to {target_date}.")

    # 4. Feature Extraction
    print(f"\n[Step 3] Building Leak-Free Features...")
    builder = FeatureBuilder()
    features_df = builder.build_features(
        recent_grid, 
        staff_df=cdata["staff"], 
        phc_meta=cdata["phcs"], 
        neighbors=cdata["neighbors"]
    )
    print(f"   [OK] Generated {features_df.shape[1]} features.")

    # Format date as standard YYYY-MM-DD string for reliable matching
    features_df["date"] = pd.to_datetime(features_df["date"]).dt.strftime("%Y-%m-%d")

    # 5. Extract Today's Target Rows
    today_feat = features_df[features_df["date"] == target_date].copy().reset_index(drop=True)
    if today_feat.empty:
        print(f"   [INFO] Exact target date '{target_date}' not found in feature rows, selecting latest available date.")
        latest_date = features_df["date"].max()
        today_feat = features_df[features_df["date"] == latest_date].copy().reset_index(drop=True)
        target_date = latest_date

    print(f"   [OK] Extracted {len(today_feat)} rows for inference on date {target_date}.")

    # 6. Multi-Horizon Quantile Forecasting
    print(f"\n[Step 4] Forecasting 7-Day Demand Quantiles (P10, P50, P90)...")
    # Train forecaster on historical slice (excluding target date)
    train_slice = features_df[features_df["date"] < target_date].dropna().reset_index(drop=True)
    if len(train_slice) > 100:
        forecaster = LightGBMForecaster(n_estimators=40, learning_rate=0.08)
        forecaster.fit(train_slice)
        q_preds = forecaster.predict(today_feat)
    else:
        # Fallback multi-quantile estimate if slice is small
        p50 = np.maximum(1.0, today_feat["consumed_units"].values)[:, None]
        q_preds = np.tile(p50[:, :, None], (1, 7, 3)).astype(np.float64)
        q_preds[:, :, 0] *= 0.85
        q_preds[:, :, 2] *= 1.25

    print(f"   [OK] Generated 7-day quantile matrix of shape {q_preds.shape}.")

    # 7. Anomaly & Outbreak Pattern Detection
    print(f"\n[Step 5] Running Anomaly & Outbreak Pattern Detectors...")
    anomaly_detector = LayeredAnomalyDetector()
    history_demand = train_slice["consumed_units"].values if len(train_slice) > 50 else today_feat["consumed_units"].values
    anomaly_detector.fit(train_slice if len(train_slice) > 50 else today_feat, history_demand)
    
    p50_preds_h1 = q_preds[:, 0, 1]
    anom_scores, detected, anom_types = anomaly_detector.detect(today_feat, p50_preds_h1)

    med_list = cdata["medicines"].get("medicines", []) if isinstance(cdata["medicines"], dict) else cdata["medicines"]
    phc_list = cdata["phcs"].get("phcs", []) if isinstance(cdata["phcs"], dict) else cdata["phcs"]

    pattern_detector = MultiResourcePatternDetector()
    alerts = pattern_detector.detect_patterns(today_feat, anom_scores, med_list)
    print(f"   [OK] Detected {np.sum(detected)} anomalies and {len(alerts)} outbreak alerts.")

    # 8. Generate Sharma Redistribution Contract Records
    print(f"\n[Step 6] Compiling Exact Sharma Redistribution JSON Contract...")
    service = PredictionService(planning_horizon_days=7)
    sharma_records = service.generate_sharma_records(
        df=today_feat,
        forecast_quantiles=q_preds,
        anomaly_scores=anom_scores,
        anomaly_detected=detected,
        med_catalog=med_list,
        phc_catalog=phc_list
    )
    print(f"   [OK] Compiled {len(sharma_records)} redistribution records.")

    # 9. Save Output Files
    print(f"\n[Step 7] Exporting Output JSON Files...")
    
    # Save Sharma Redistribution Predictions
    os.makedirs(os.path.dirname(os.path.abspath(output_predictions_path)), exist_ok=True)
    with open(output_predictions_path, "w", encoding="utf-8") as f:
        json.dump(sharma_records, f, indent=2)
    print(f"   [OK] Saved Sharma Predictions JSON: {output_predictions_path} ({len(sharma_records)} items)")

    # Save Outbreak Alerts
    os.makedirs(os.path.dirname(os.path.abspath(output_alerts_path)), exist_ok=True)
    with open(output_alerts_path, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
    print(f"   [OK] Saved Disease Alerts JSON:     {output_alerts_path} ({len(alerts)} alerts)")

    # 10. Print Summary to Console
    print("\n" + "=" * 80)
    print(f"  DAILY PREDICTION SUMMARY -- {country.upper()} ({target_date})")
    print("=" * 80)
    
    high_risk_recs = [r for r in sharma_records if r["risk"]["level"] == "HIGH"]
    med_risk_recs = [r for r in sharma_records if r["risk"]["level"] == "MEDIUM"]
    low_risk_recs = [r for r in sharma_records if r["risk"]["level"] == "LOW"]

    print(f"Total Facilities / Items Evaluated : {len(sharma_records)}")
    print(f"Risk Breakdown                      : HIGH: {len(high_risk_recs)} | MEDIUM: {len(med_risk_recs)} | LOW: {len(low_risk_recs)}")
    print(f"Outbreak Early Warning Alerts       : {len(alerts)}")

    if high_risk_recs:
        print("\nTop High Risk Items Flagged for Redistribution:")
        for r in high_risk_recs[:5]:
            print(f" * [{r['phc_id']}] {r['medicine_name']}: Stock={r['current_stock']} {r['unit']}, "
                  f"Days to Stockout={r['stockout']['estimated_days']}d (Est: {r['stockout']['estimated_date']}), "
                  f"RiskScore={r['risk']['score']}, SafetyStock={r['inventory_protection']['safety_stock']}")

    if alerts:
        print("\nActive Disease / Outbreak Pattern Alerts:")
        for a in alerts[:3]:
            print(f" ! [{a['severity']}] {a['pattern_type']} at {a['phc_id']} (Confidence: {a['confidence_score']}): "
                  f"Driver: {a['primary_driver']}, Correlated: {', '.join(a['correlated_resources'])}")

    print("\n[SUCCESS] Daily pipeline completed. Files ready for Sharma Redistribution Engine.")
    print("=" * 80)

    return {
        "country": country,
        "date": target_date,
        "sharma_records": sharma_records,
        "alerts": alerts,
        "output_predictions": output_predictions_path,
        "output_alerts": output_alerts_path
    }


def main():
    parser = argparse.ArgumentParser(description="Daily operational ingestion, ML forecasting, and Sharma JSON export.")
    parser.add_argument("--input", "-i", type=str, default="inputs/daily_input_template.json", help="Path to daily input JSON file (default: inputs/daily_input_template.json).")
    parser.add_argument("--country", "-c", type=str, default=None, help="Override country (india, brazil, south_africa, china, russia).")
    parser.add_argument("--output_predictions", "-p", type=str, default="outputs/predictions/predictions.json", help="Path to save predictions JSON.")
    parser.add_argument("--output_alerts", "-a", type=str, default="outputs/alerts/alerts.json", help="Path to save alerts JSON.")
    parser.add_argument("--base_dir", "-b", type=str, default="data", help="Base dataset directory.")
    parser.add_argument("--dry_run", action="store_true", help="Run inference without modifying CSV files.")

    args = parser.parse_args()

    run_daily_prediction_pipeline(
        input_file=args.input,
        country_override=args.country,
        output_predictions_path=args.output_predictions,
        output_alerts_path=args.output_alerts,
        base_dir=args.base_dir,
        dry_run=args.dry_run
    )


if __name__ == "__main__":
    main()
