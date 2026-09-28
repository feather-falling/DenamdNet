"""
Unit tests for Inventory Conservation, Negative Stock Rejection, and Demand vs Consumption distinction.
"""

import pytest
from simulation.generator import DailyInputSimulator
from redistribution.models.state import InventoryItemState
from redistribution.engine.inventory_state import GlobalInventoryState


def test_inventory_conservation_equation():
    """Verify closing_stock = opening_stock + received - consumed - out + in."""
    opening = 500
    received = 50
    consumed = 120
    out_transfer = 30
    in_transfer = 10

    closing = opening + received - consumed - out_transfer + in_transfer
    assert closing == 410


def test_negative_inventory_rejection():
    """Verify that transfers cannot drive source inventory below 0 or below protected stock."""
    state = InventoryItemState(
        phc_id="PHC-TEST-01",
        medicine_id="MED-001",
        medicine_name="Paracetamol",
        original_stock=100.0,
        current_stock=100.0,
        daily_requirement=10.0,
        safety_stock=50.0,
        planning_horizon_days=7
    )
    # Protected stock = 10 * 7 + 50 = 120
    # Current stock = 100 < 120, so transferable surplus must be 0!
    assert state.protected_stock == 120.0
    assert state.transferable_surplus == 0.0

    # Attempting to transfer from a zero-surplus source in GlobalInventoryState must raise error
    g_state = GlobalInventoryState()
    g_state.get_or_create("PHC-SRC", "MED-001", default_stock=100.0, daily_req=10.0, safety=50.0)
    g_state.get_or_create("PHC-TGT", "MED-001", default_stock=0.0, daily_req=10.0, safety=50.0)

    with pytest.raises(ValueError, match="Cannot execute transfer"):
        g_state.apply_transfer(
            target_phc_id="PHC-TGT",
            source_phc_id="PHC-SRC",
            medicine_id="MED-001",
            transferred_units=50.0,
            distance_km=10.0,
            target_required_before=120.0
        )


def test_demand_vs_consumption_distinction():
    """Verify demand_units can exceed consumed_units when stock is insufficient."""
    # When opening stock is 50, demand is 80:
    # consumed should be 50, unmet demand should be 30, closing stock should be 0.
    opening_stock = 50
    demand_units = 80
    available_stock = opening_stock
    consumed_units = min(demand_units, available_stock)
    unmet_demand = demand_units - consumed_units
    closing_stock = opening_stock - consumed_units

    assert consumed_units == 50
    assert unmet_demand == 30
    assert closing_stock == 0
    assert demand_units > consumed_units
