"""
Surplus calculation module.
Computes protected stock and transferable surplus strictly adhering to:
protected_stock = daily_requirement * planning_horizon + safety_stock
transferable_surplus = max(0, current_stock - protected_stock)
"""

from typing import Optional
from ..models.state import InventoryItemState


class SurplusCalculator:
    """Calculates protected stock and transferable surplus for candidate source facilities."""

    @staticmethod
    def calculate_protected_stock(
        daily_requirement: float,
        safety_stock: float,
        planning_horizon_days: int = 7
    ) -> float:
        """Calculates protected threshold below which stock must not be transferred."""
        return (daily_requirement * planning_horizon_days) + safety_stock

    @staticmethod
    def calculate_transferable_surplus(
        current_stock: float,
        daily_requirement: float,
        safety_stock: float,
        planning_horizon_days: int = 7
    ) -> float:
        """Calculates quantity available for transfer without breaching protection."""
        protected = SurplusCalculator.calculate_protected_stock(
            daily_requirement, safety_stock, planning_horizon_days
        )
        return max(0.0, current_stock - protected)

    @staticmethod
    def get_source_surplus(state: InventoryItemState) -> float:
        """Calculates transferable surplus directly from an InventoryItemState instance."""
        return state.transferable_surplus
