"""
CLI Entrypoint for the BRICS PHC Redistribution Engine.
Reads alerts, predictions, input_today, and network topology,
allocates transfers, and exports results.
"""

import os
import sys
import argparse

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from redistribution.engine.redistribution_engine import RedistributionEngine


def main():
    parser = argparse.ArgumentParser(description="Run BRICS PHC Redistribution Engine.")
    parser.add_argument("--country", "-c", type=str, default=None, help="Country override (india, brazil, south_africa, china, russia).")
    parser.add_argument("--alerts", "-a", type=str, default=None, help="Path to alerts.json.")
    parser.add_argument("--predictions", "-p", type=str, default=None, help="Path to predictions.json.")
    parser.add_argument("--input", "-i", type=str, default=None, help="Path to input_today.json.")
    parser.add_argument("--output_dir", "-o", type=str, default="output/redistribution", help="Directory to save redistribution outputs.")
    parser.add_argument("--base_dir", "-b", type=str, default="data", help="Base dataset directory.")

    args = parser.parse_args()

    print("=" * 80)
    print("  BRICS HEALTH & SUPPLY CHAIN RESILIENCE -- REDISTRIBUTION ENGINE")
    print("=" * 80)

    engine = RedistributionEngine(
        base_dir=args.base_dir,
        output_dir=args.output_dir
    )

    result = engine.run(
        country=args.country,
        alerts_path=args.alerts,
        predictions_path=args.predictions,
        input_today_path=args.input,
        save_outputs=True
    )

    summary = result.summary_dict()
    print(f"\nRedistribution Completed for Country: [{result.country.upper()}]")
    print(f"Total Targets Evaluated : {summary['total_targets_evaluated']} (Alert Priority: {summary['alert_priority_targets']})")
    print(f"Transfers Executed      : {summary['total_transfers_executed']}")
    print(f"Total Volume Transferred: {summary['total_volume_transferred']} units")
    print(f"Resolution Breakdown    : Fully Resolved: {summary['fully_resolved_count']} | "
          f"Partially Resolved: {summary['partially_resolved_count']} | "
          f"Unresolved: {summary['unresolved_count']}")

    if result.transfers_executed:
        print("\nSample Simulated Transfers:")
        for t in result.transfers_executed[:5]:
            print(f" * [{t.source_phc_id}] -> [{t.target_phc_id}] | {t.medicine_name}: {t.transferred_units} units ({t.distance_km} km) [{t.status}]")

    if result.unresolved_requirements:
        print(f"\nUnresolved / Partially Resolved Shortages: {len(result.unresolved_requirements)}")
        for u in result.unresolved_requirements[:3]:
            print(f" ! [{u.target_phc_id}] {u.medicine_name}: Missing {u.remaining_requirement} units ({u.status})")

    print(f"\n[SUCCESS] Output files written to '{args.output_dir}' and 'outputs/redistribution/'.")
    print("  - next_day_phc_data.json")
    print("  - redistribution_results.json")
    print("  - unresolved_requirements.json")
    print("=" * 80)


if __name__ == "__main__":
    main()
