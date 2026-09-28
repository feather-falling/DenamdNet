"""
Mutable in-memory inventory state manager.
Maintains a single shared global inventory state across all target facilities during a redistribution run.
"""

from typing import Dict, Any, List, Optional, Tuple
from ..models.state import InventoryItemState, TransferRecord


class GlobalInventoryState:
    """Shared in-memory inventory state for all PHC x Medicine combinations in the network.
    
    Guarantees:
    - Never resets between targets.
    - Prevents double-donating the same inventory.
    - Updates source and target immediately upon any transfer.
    - Preserves total global inventory conservation.
    """

    def __init__(self):
        # Key: (phc_id, medicine_id) -> InventoryItemState
        self._state: Dict[Tuple[str, str], InventoryItemState] = {}
        # Metadata lookup
        self._phc_meta: Dict[str, Dict[str, Any]] = {}
        self._med_meta: Dict[str, Dict[str, Any]] = {}

    def initialize(
        self,
        phcs: List[Dict[str, Any]],
        medicines: List[Dict[str, Any]],
        input_records: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]],
        default_planning_horizon: int = 7
    ) -> None:
        """Initializes state for every facility and medicine in the network."""
        self._state.clear()
        self._phc_meta = {p["phc_id"]: p for p in phcs}
        self._med_meta = {m["medicine_id"]: m for m in medicines}

        # Build quick lookups for input telemetry and predictions
        input_lookup = {
            (r["phc_id"], r["medicine_id"]): r for r in input_records
        }
        pred_lookup = {
            (p["phc_id"], p["medicine_id"]): p for p in predictions
        }

        # Also map medicine name -> medicine_id for name-based lookup
        name_to_id = {m.get("name", "").strip().lower(): m["medicine_id"] for m in medicines}

        for phc in phcs:
            phc_id = phc["phc_id"]
            phc_district = phc.get("district", "")
            phc_state = phc.get("state", phc.get("state_region", ""))
            country_code = phc.get("country_code", "IN")

            for med in medicines:
                med_id = med["medicine_id"]
                med_name = med.get("name", med_id)

                # 1. Opening stock: from input_today.json record if available
                inp_rec = input_lookup.get((phc_id, med_id))
                pred_rec = pred_lookup.get((phc_id, med_id))

                if inp_rec is not None:
                    # Closing stock of input_today represents the current starting operational stock
                    orig_stock = float(inp_rec.get("closing_stock", inp_rec.get("opening_stock", 0.0)))
                elif pred_rec is not None:
                    orig_stock = float(pred_rec.get("current_stock", 0.0))
                else:
                    orig_stock = 0.0

                # 2. Daily requirement & Safety stock: from predictions if available, else catalog
                if pred_rec is not None:
                    daily_req = float(pred_rec.get("forecast_demand", {}).get("daily", 10.0))
                    horizon = int(pred_rec.get("forecast_demand", {}).get("planning_horizon_days", default_planning_horizon))
                    safety = float(pred_rec.get("inventory_protection", {}).get("safety_stock", 10.0))
                    country_code = pred_rec.get("country_code", country_code)
                    phc_district = pred_rec.get("district", phc_district)
                    phc_state = pred_rec.get("state_region", phc_state)
                else:
                    scale = float(med.get("simulation_profile", {}).get("base_daily_demand_scale", 20.0))
                    daily_req = max(1.0, scale if scale >= 5.0 else scale * 30.0)
                    horizon = default_planning_horizon
                    safety = max(5.0, round(daily_req * 0.2))

                item_state = InventoryItemState(
                    phc_id=phc_id,
                    medicine_id=med_id,
                    medicine_name=med_name,
                    original_stock=orig_stock,
                    current_stock=orig_stock,
                    daily_requirement=daily_req,
                    safety_stock=safety,
                    planning_horizon_days=horizon,
                    incoming_units=0.0,
                    outgoing_units=0.0,
                    country_code=country_code,
                    district=phc_district,
                    state_region=phc_state
                )
                self._state[(phc_id, med_id)] = item_state

    def get(self, phc_id: str, medicine_id: str) -> Optional[InventoryItemState]:
        """Retrieves item state for given (phc_id, medicine_id)."""
        return self._state.get((phc_id, medicine_id))

    def get_or_create(
        self,
        phc_id: str,
        medicine_id: str,
        default_stock: float = 0.0,
        daily_req: float = 10.0,
        safety: float = 10.0
    ) -> InventoryItemState:
        """Retrieves or creates state for testing or dynamically added pairs."""
        key = (phc_id, medicine_id)
        if key not in self._state:
            self._state[key] = InventoryItemState(
                phc_id=phc_id,
                medicine_id=medicine_id,
                medicine_name=medicine_id,
                original_stock=default_stock,
                current_stock=default_stock,
                daily_requirement=daily_req,
                safety_stock=safety,
                planning_horizon_days=7,
                incoming_units=0.0,
                outgoing_units=0.0
            )
        return self._state[key]

    def apply_transfer(
        self,
        target_phc_id: str,
        source_phc_id: str,
        medicine_id: str,
        transferred_units: float,
        distance_km: float,
        target_required_before: float
    ) -> TransferRecord:
        """Executes an atomic transfer between source and target, immediately modifying shared state.
        
        Guarantees:
        - source.current_stock decreases by transferred_units
        - source.outgoing_units increases by transferred_units
        - target.current_stock increases by transferred_units
        - target.incoming_units increases by transferred_units
        """
        source_state = self.get(source_phc_id, medicine_id)
        target_state = self.get(target_phc_id, medicine_id)

        if not source_state:
            raise KeyError(f"Source state not found for {source_phc_id}, {medicine_id}")
        if not target_state:
            raise KeyError(f"Target state not found for {target_phc_id}, {medicine_id}")

        surplus_before = source_state.transferable_surplus
        # Validate that transferred_units does not exceed available surplus
        actual_units = min(transferred_units, surplus_before)
        if actual_units <= 0:
            raise ValueError(f"Cannot execute transfer of {transferred_units} units from source with surplus {surplus_before}")

        # Update source
        source_state.current_stock -= actual_units
        source_state.outgoing_units += actual_units

        # Update target
        target_state.current_stock += actual_units
        target_state.incoming_units += actual_units

        # Calculate remaining values
        remaining_target_req = max(0.0, target_required_before - actual_units)
        remaining_source_surplus = source_state.transferable_surplus

        status = "RESOLVED" if remaining_target_req <= 1e-4 else "PARTIALLY_RESOLVED"

        return TransferRecord(
            target_phc_id=target_phc_id,
            source_phc_id=source_phc_id,
            medicine_id=medicine_id,
            medicine_name=target_state.medicine_name,
            required_units_before_transfer=target_required_before,
            source_transferable_surplus_before_transfer=surplus_before,
            transferred_units=actual_units,
            distance_km=distance_km,
            remaining_target_requirement=remaining_target_req,
            source_remaining_transferable_surplus=remaining_source_surplus,
            status=status
        )

    def export_all_states(self) -> List[Dict[str, Any]]:
        """Exports complete operational state for ALL facilities and ALL medicines."""
        sorted_keys = sorted(self._state.keys())
        return [self._state[k].to_dict() for k in sorted_keys]

    def all_items(self) -> List[InventoryItemState]:
        """Returns list of all InventoryItemState instances."""
        return list(self._state.values())
