"""
Transfer calculation module.
Allocates transfer units between donor and recipient, ensuring source never drops below protected stock.
"""

from typing import Optional, Tuple
from ..models.state import TargetRequirement, TransferRecord
from .inventory_state import GlobalInventoryState


class TransferCalculator:
    """Calculates and executes simulated transfers while preserving inventory invariants."""

    @staticmethod
    def execute_transfer(
        target: TargetRequirement,
        source_phc_id: str,
        distance_km: float,
        global_state: GlobalInventoryState
    ) -> Optional[TransferRecord]:
        """Calculates transfer amount min(target_remaining, source_surplus) and updates global state immediately.
        
        Returns TransferRecord if a transfer took place, else None.
        """
        if target.remaining_requirement <= 1e-4:
            return None

        source_state = global_state.get(source_phc_id, target.medicine_id)
        if not source_state:
            return None

        surplus = source_state.transferable_surplus
        if surplus <= 1e-4:
            return None

        # Determine transfer units
        transfer_units = min(target.remaining_requirement, surplus)
        if transfer_units <= 0:
            return None

        # Execute on shared global inventory state
        transfer_record = global_state.apply_transfer(
            target_phc_id=target.phc_id,
            source_phc_id=source_phc_id,
            medicine_id=target.medicine_id,
            transferred_units=transfer_units,
            distance_km=distance_km,
            target_required_before=target.remaining_requirement
        )

        # Update target requirement remaining units
        target.remaining_requirement -= transfer_units
        return transfer_record
