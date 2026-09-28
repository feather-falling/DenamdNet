"""
Unit tests for Transfers and Shared Global State.
"""

from redistribution.engine.inventory_state import GlobalInventoryState
from redistribution.engine.transfer_calculator import TransferCalculator
from redistribution.models.state import TargetRequirement


def test_full_transfer():
    """Single source has enough surplus to fully satisfy target."""
    state = GlobalInventoryState()
    # Source: stock=2000, daily=100, safety=100 -> protected=800, surplus=1200
    state.get_or_create("SRC-1", "MED-1", default_stock=2000.0, daily_req=100.0, safety=100.0)
    # Target: stock=0, daily=50, safety=50 -> protected=400, required=400
    state.get_or_create("TGT-1", "MED-1", default_stock=0.0, daily_req=50.0, safety=50.0)

    target_req = TargetRequirement(
        country_code="IN",
        phc_id="TGT-1",
        medicine_id="MED-1",
        medicine_name="Paracetamol",
        district="D1",
        state_region="S1",
        initial_stock=0.0,
        daily_forecast=50.0,
        safety_stock=50.0,
        planning_horizon_days=7,
        target_required_units=400.0,
        remaining_requirement=400.0
    )

    transfer = TransferCalculator.execute_transfer(
        target=target_req,
        source_phc_id="SRC-1",
        distance_km=15.0,
        global_state=state
    )

    assert transfer is not None
    assert transfer.transferred_units == 400.0
    assert transfer.status == "RESOLVED"
    assert target_req.remaining_requirement == 0.0

    # Source must have decreased by 400, target increased by 400
    assert state.get("SRC-1", "MED-1").current_stock == 1600.0
    assert state.get("TGT-1", "MED-1").current_stock == 400.0


def test_partial_transfer():
    """Source has less surplus than target requires."""
    state = GlobalInventoryState()
    # Source: stock=1000, daily=100, safety=100 -> protected=800, surplus=200
    state.get_or_create("SRC-1", "MED-1", default_stock=1000.0, daily_req=100.0, safety=100.0)
    # Target requires 500
    state.get_or_create("TGT-1", "MED-1", default_stock=0.0, daily_req=50.0, safety=50.0)

    target_req = TargetRequirement(
        country_code="IN",
        phc_id="TGT-1",
        medicine_id="MED-1",
        medicine_name="Paracetamol",
        district="D1",
        state_region="S1",
        initial_stock=0.0,
        daily_forecast=50.0,
        safety_stock=50.0,
        planning_horizon_days=7,
        target_required_units=500.0,
        remaining_requirement=500.0
    )

    transfer = TransferCalculator.execute_transfer(
        target=target_req,
        source_phc_id="SRC-1",
        distance_km=10.0,
        global_state=state
    )

    assert transfer.transferred_units == 200.0
    assert transfer.status == "PARTIALLY_RESOLVED"
    assert target_req.remaining_requirement == 300.0
    assert state.get("SRC-1", "MED-1").current_stock == 800.0  # Exactly at protected threshold
    assert state.get("SRC-1", "MED-1").transferable_surplus == 0.0


def test_multiple_sources_satisfying_single_target():
    """Target requires 500. Source A has 300 surplus, Source B has 200 surplus."""
    state = GlobalInventoryState()
    # Source A: protected=800, stock=1100 -> surplus=300
    state.get_or_create("SRC-A", "MED-1", default_stock=1100.0, daily_req=100.0, safety=100.0)
    # Source B: protected=800, stock=1000 -> surplus=200
    state.get_or_create("SRC-B", "MED-1", default_stock=1000.0, daily_req=100.0, safety=100.0)
    # Target
    state.get_or_create("TGT-1", "MED-1", default_stock=0.0, daily_req=60.0, safety=80.0)

    target_req = TargetRequirement(
        country_code="IN",
        phc_id="TGT-1",
        medicine_id="MED-1",
        medicine_name="Paracetamol",
        district="D1",
        state_region="S1",
        initial_stock=0.0,
        daily_forecast=60.0,
        safety_stock=80.0,
        planning_horizon_days=7,
        target_required_units=500.0,
        remaining_requirement=500.0
    )

    t1 = TransferCalculator.execute_transfer(target_req, "SRC-A", 10.0, state)
    assert t1.transferred_units == 300.0
    assert target_req.remaining_requirement == 200.0

    t2 = TransferCalculator.execute_transfer(target_req, "SRC-B", 20.0, state)
    assert t2.transferred_units == 200.0
    assert target_req.remaining_requirement == 0.0
    assert t2.status == "RESOLVED"

    assert state.get("TGT-1", "MED-1").current_stock == 500.0
    assert state.get("SRC-A", "MED-1").current_stock == 800.0
    assert state.get("SRC-B", "MED-1").current_stock == 800.0


def test_shared_global_inventory_state_no_double_donations():
    """Source X surplus = 1000. Target A receives 700. Source X remaining surplus = 300.
    Target B requesting 500 can receive at most 300.
    """
    state = GlobalInventoryState()
    # Source X: protected=1000, stock=2000 -> surplus=1000
    state.get_or_create("SRC-X", "MED-1", default_stock=2000.0, daily_req=100.0, safety=300.0)
    state.get_or_create("TGT-A", "MED-1", default_stock=0.0, daily_req=100.0, safety=0.0)
    state.get_or_create("TGT-B", "MED-1", default_stock=0.0, daily_req=100.0, safety=0.0)

    # Target A requires 700
    req_a = TargetRequirement(
        country_code="IN", phc_id="TGT-A", medicine_id="MED-1", medicine_name="M",
        district="D", state_region="S", initial_stock=0.0, daily_forecast=100.0,
        safety_stock=0.0, planning_horizon_days=7, target_required_units=700.0,
        remaining_requirement=700.0
    )
    t_a = TransferCalculator.execute_transfer(req_a, "SRC-X", 10.0, state)
    assert t_a.transferred_units == 700.0
    assert state.get("SRC-X", "MED-1").transferable_surplus == 300.0

    # Target B requires 500
    req_b = TargetRequirement(
        country_code="IN", phc_id="TGT-B", medicine_id="MED-1", medicine_name="M",
        district="D", state_region="S", initial_stock=0.0, daily_forecast=100.0,
        safety_stock=0.0, planning_horizon_days=7, target_required_units=500.0,
        remaining_requirement=500.0
    )
    t_b = TransferCalculator.execute_transfer(req_b, "SRC-X", 15.0, state)
    # Can receive AT MOST 300!
    assert t_b.transferred_units == 300.0
    assert state.get("SRC-X", "MED-1").current_stock == 1000.0  # Protected threshold
    assert state.get("SRC-X", "MED-1").transferable_surplus == 0.0
    assert req_b.remaining_requirement == 200.0
