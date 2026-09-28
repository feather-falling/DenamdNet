import pytest
import sys, os
sys.path.insert(0, os.path.abspath("ai-ml"))

import pandas as pd
import numpy as np
from simulation.closed_loop import ClosedLoopSimulation

def test_closed_loop_simulation():
    initial_df = pd.DataFrame([{
        "date": "2026-09-18",
        "phc_id": "IN-UP-MEE-001",
        "medicine_id": "MED-001",
        "opening_stock": 500.0,
        "received_units": 0.0,
        "consumed_units": 100.0,
        "outgoing_transfer_units": 0.0,
        "incoming_transfer_units": 0.0,
        "closing_stock": 400.0,
        "demand_units": 100.0,
        "unmet_demand_units": 0.0
    }])

    sim = ClosedLoopSimulation(initial_df)
    res = sim.run_simulation(steps=2)

    assert res["steps_completed"] == 2
    assert len(res["simulation_history"]) == 2
