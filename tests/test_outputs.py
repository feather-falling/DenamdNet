"""
Unit tests for Output File Structures, completeness, and non-modification of input_today.json.
"""

import os
import json
import pytest
from redistribution.engine.redistribution_engine import RedistributionEngine


def test_redistribution_outputs_completeness(tmp_path):
    """Verify that next_day_phc_data.json contains every facility and medicine in network,
    and output files are correctly structured.
    """
    out_dir = str(tmp_path / "redistribution")
    engine = RedistributionEngine(output_dir=out_dir)

    result = engine.run(save_outputs=True)

    # 1. next_day_phc_data.json exists and has all items
    next_day_file = os.path.join(out_dir, "next_day_phc_data.json")
    assert os.path.exists(next_day_file)
    with open(next_day_file, "r") as f:
        next_day_data = json.load(f)

    # India dataset has 54 PHCs x 18 medicines = 972 (or 2934 for 3 countries, 4878 for 5 countries)
    assert len(next_day_data) in [972, 2934, 4878]

    first_item = next_day_data[0]
    required_keys = [
        "phc_id", "medicine_id", "original_stock", "incoming_units",
        "outgoing_units", "final_stock", "daily_requirement",
        "protected_stock", "remaining_requirement", "status"
    ]
    for k in required_keys:
        assert k in first_item

    # 2. redistribution_results.json exists and has summary + transfers
    results_file = os.path.join(out_dir, "redistribution_results.json")
    assert os.path.exists(results_file)
    with open(results_file, "r") as f:
        results_data = json.load(f)
    assert "summary" in results_data
    assert "transfers" in results_data

    # 3. unresolved_requirements.json exists
    unresolved_file = os.path.join(out_dir, "unresolved_requirements.json")
    assert os.path.exists(unresolved_file)


def test_original_input_not_modified():
    """Verify that input/input_today.json content is identical before and after redistribution."""
    input_file = os.path.join("input", "input_today.json")
    if not os.path.exists(input_file):
        pytest.skip("input/input_today.json not found")

    with open(input_file, "r", encoding="utf-8") as f:
        content_before = f.read()

    engine = RedistributionEngine(output_dir="output/redistribution")
    engine.run(input_today_path=input_file, save_outputs=False)

    with open(input_file, "r", encoding="utf-8") as f:
        content_after = f.read()

    assert content_before == content_after, "Redistribution engine must NEVER modify input_today.json!"
