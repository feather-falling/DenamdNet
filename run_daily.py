"""
Unified Daily Orchestration CLI.
Executes the end-to-end workflow:
1. Daily Operational Telemetry Ingestion / ML Forecasting (ai-ml/run_daily_prediction.py)
2. Network Redistribution Engine (redistribution/run_redistribution.py)
"""

import sys
import os
import argparse

# Ensure project root is first on sys.path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
AIML_DIR = os.path.join(PROJECT_ROOT, "ai-ml")
if AIML_DIR not in sys.path:
    sys.path.append(AIML_DIR)
if sys.path[0] != PROJECT_ROOT:
    sys.path.insert(0, PROJECT_ROOT)

from simulation.generator import DailyInputSimulator
from run_daily_prediction import run_daily_prediction_pipeline
from redistribution.engine.redistribution_engine import RedistributionEngine



def main():
    parser = argparse.ArgumentParser(description="Orchestrate daily ML prediction and redistribution flow.")
    parser.add_argument("--country", "-c", type=str, default="india", help="Country (india, brazil, south_africa, china, russia, all).")
    parser.add_argument("--input", "-i", type=str, default="input/input_today.json", help="Path to input_today.json.")
    parser.add_argument("--simulate", "-s", action="store_true", help="Generate fresh input_today.json before running.")
    parser.add_argument("--date", "-d", type=str, default=None, help="Target date YYYY-MM-DD.")
    parser.add_argument("--dry_run", action="store_true", help="Skip appending to country historical CSVs.")

    args = parser.parse_args()

    print("=" * 80)
    print("  BRICS HEALTH & SUPPLY CHAIN RESILIENCE -- DAILY ORCHESTRATION")
    print("=" * 80)

    # 1. Optionally simulate fresh input telemetry
    if args.simulate or not os.path.exists(args.input):
        print(f"\n[Step 0] Generating complete input telemetry for country='{args.country}'...")
        simulator = DailyInputSimulator()
        if args.country.lower() in ["all", "global", "multi", "multicountry"]:
            telemetry, dist_stats = simulator.generate_multicountry_scenario(target_date=args.date or "2026-10-02")
        else:
            telemetry = simulator.generate_daily_input(country=args.country, date_str=args.date)
        saved = simulator.save_daily_input(telemetry, output_paths=[args.input, "inputs/input_today.json"])
        print(f"   [OK] Saved telemetry to {saved}")

    # 2. Run existing daily prediction pipeline
    print(f"\n[Step 1] Running Daily ML Forecasting & Anomaly Pipeline...")
    ml_res = run_daily_prediction_pipeline(
        input_file=args.input,
        country_override=args.country,
        output_predictions_path="output/alerts/predictions.json",
        output_alerts_path="output/alerts/alerts.json",
        dry_run=args.dry_run
    )

    # Also sync outputs to outputs/ folder for backward compatibility
    import shutil
    os.makedirs("outputs/alerts", exist_ok=True)
    os.makedirs("outputs/predictions", exist_ok=True)
    shutil.copy("output/alerts/alerts.json", "outputs/alerts/alerts.json")
    shutil.copy("output/alerts/predictions.json", "outputs/predictions/predictions.json")

    # 3. Run Redistribution Engine
    print(f"\n[Step 2] Running Network Redistribution Engine...")
    engine = RedistributionEngine(output_dir="output/redistribution")
    result = engine.run(
        country=args.country,
        alerts_path="output/alerts/alerts.json",
        predictions_path="output/alerts/predictions.json",
        input_today_path=args.input,
        save_outputs=True
    )

    # 4. Summary
    summary = result.summary_dict()
    print("\n" + "=" * 80)
    print(f"  COMPLETE DAILY ORCHESTRATION SUMMARY -- {args.country.upper()}")
    print("=" * 80)
    print(f"ML Forecast Records Evaluated : {len(ml_res.get('sharma_records', []))}")
    print(f"Early Warning Disease Alerts   : {len(ml_res.get('alerts', []))}")
    print(f"Redistribution Targets Flagged : {summary['total_targets_evaluated']} (Alert Priority: {summary['alert_priority_targets']})")
    print(f"Transfers Executed             : {summary['total_transfers_executed']}")
    print(f"Total Stock Volume Transferred : {summary['total_volume_transferred']} units")
    print(f"Resolution Breakdown           : Fully Resolved: {summary['fully_resolved_count']} | "
          f"Partially Resolved: {summary['partially_resolved_count']} | "
          f"Unresolved: {summary['unresolved_count']}")
    print("\n[SUCCESS] End-to-end daily operational orchestration finished successfully.")
    print("=" * 80)


if __name__ == "__main__":
    main()
