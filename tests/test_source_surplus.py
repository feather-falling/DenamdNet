"""
Unit tests for Source Surplus Calculation.
"""

from redistribution.engine.surplus_calculator import SurplusCalculator
from redistribution.models.state import InventoryItemState


def test_surplus_source_calculation():
    """Verify surplus source: current=5000, daily=100, safety=300 -> protected=1000, surplus=4000."""
    protected = SurplusCalculator.calculate_protected_stock(
        daily_requirement=100.0,
        safety_stock=300.0,
        planning_horizon_days=7
    )
    assert protected == 1000.0

    surplus = SurplusCalculator.calculate_transferable_surplus(
        current_stock=5000.0,
        daily_requirement=100.0,
        safety_stock=300.0,
        planning_horizon_days=7
    )
    assert surplus == 4000.0


def test_deficit_source_produces_zero_surplus():
    """If stock is below protected threshold, surplus is strictly 0.0."""
    surplus = SurplusCalculator.calculate_transferable_surplus(
        current_stock=800.0,
        daily_requirement=100.0,
        safety_stock=300.0,
        planning_horizon_days=7
    )
    assert surplus == 0.0


def test_exact_surplus_boundary():
    """If current stock exactly equals protected stock, surplus is 0.0."""
    surplus = SurplusCalculator.calculate_transferable_surplus(
        current_stock=1000.0,
        daily_requirement=100.0,
        safety_stock=300.0,
        planning_horizon_days=7
    )
    assert surplus == 0.0


def test_partial_surplus():
    """If current stock is 1500, surplus is 500."""
    surplus = SurplusCalculator.calculate_transferable_surplus(
        current_stock=1500.0,
        daily_requirement=100.0,
        safety_stock=300.0,
        planning_horizon_days=7
    )
    assert surplus == 500.0
