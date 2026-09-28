import argparse
import sys
import os

# Add root directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from simulation.generator import DailyInputSimulator


def main():
    parser = argparse.ArgumentParser(description="Generate complete operational input telemetry for EVERY PHC x EVERY MEDICINE.")
    parser.add_argument("--country", "-c", type=str, default="india", help="Country to simulate (india, brazil, south_africa, china, russia, all).")
    parser.add_argument("--date", "-d", type=str, default="2026-10-02", help="Simulation target date (YYYY-MM-DD).")
    parser.add_argument("--output", "-o", type=str, default="input/input_today.json", help="Path to write generated input JSON.")
    parser.add_argument("--seed", "-s", type=int, default=42, help="Random seed for reproducibility.")
    parser.add_argument("--base_dir", "-b", type=str, default="data", help="Base data directory.")

    args = parser.parse_args()

    simulator = DailyInputSimulator(base_dir=args.base_dir)
    print(f"Generating complete daily input for country='{args.country}' on date='{args.date}'...")
    telemetry = simulator.generate_daily_input(
        country=args.country,
        date_str=args.date,
        seed=args.seed
    )

    outputs = [args.output]
    # If user specified default input/input_today.json, also update inputs/input_today.json
    if args.output == "input/input_today.json":
        outputs.append("inputs/input_today.json")

    saved_paths = simulator.save_daily_input(telemetry, output_paths=outputs)
    print(f"[SUCCESS] Generated {len(telemetry['records'])} medicine records and {len(telemetry['staff_attendance'])} staff records.")
    for p in saved_paths:
        print(f"  -> Saved to: {p}")


if __name__ == "__main__":
    main()
