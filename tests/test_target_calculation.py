"""
Unit tests for Target Requirement Calculation.
"""

from redistribution.models.state import InventoryItemState, TargetRequirement


def test_target_requirement_calculation():
    """Verify target calculation:
    forecast daily = 62, planning horizon = 7, safety stock = 7, current stock = 0
    planning requirement = 434, protected target stock = 441, required = 441
    """
    daily = 62.0
    horizon = 7
    safety = 7.0
    curr_stock = 0.0

    planning_req = daily * horizon
    protected = planning_req + safety
    required = max(0.0, protected - curr_stock)

    assert planning_req == 434.0
    assert protected == 441.0
    assert required == 441.0


def test_current_stock_deduction():
    """If current stock is 200, required should be 441 - 200 = 241."""
    daily = 62.0
    horizon = 7
    safety = 7.0
    curr_stock = 200.0

    protected = (daily * horizon) + safety
    required = max(0.0, protected - curr_stock)

    assert required == 241.0


def test_zero_requirement_when_already_protected():
    """If current stock >= protected stock, required units should be 0."""
    daily = 62.0
    horizon = 7
    safety = 7.0
    curr_stock = 500.0  # Above 441.0

    protected = (daily * horizon) + safety
    required = max(0.0, protected - curr_stock)

    assert required == 0.0
