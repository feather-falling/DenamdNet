"""
Data models and state definitions for the Redistribution Engine.
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class InventoryItemState:
    """Represents mutable in-memory inventory state for a single (phc_id, medicine_id) pair."""
    phc_id: str
    medicine_id: str
    medicine_name: str
    original_stock: float
    current_stock: float
    daily_requirement: float
    safety_stock: float
    planning_horizon_days: int = 7
    incoming_units: float = 0.0
    outgoing_units: float = 0.0
    country_code: str = ""
    district: str = ""
    state_region: str = ""

    @property
    def protected_stock(self) -> float:
        """Protected stock threshold: daily_requirement * planning_horizon + safety_stock."""
        return (self.daily_requirement * self.planning_horizon_days) + self.safety_stock

    @property
    def transferable_surplus(self) -> float:
        """Transferable surplus available to donate without breaching protected stock."""
        return max(0.0, self.current_stock - self.protected_stock)

    @property
    def required_units(self) -> float:
        """Shortage required to reach protected stock."""
        return max(0.0, self.protected_stock - self.current_stock)

    @property
    def status(self) -> str:
        """Current operational status."""
        if self.current_stock >= self.protected_stock:
            if self.incoming_units > 0:
                return "RESOLVED"
            return "HEALTHY"
        elif self.incoming_units > 0:
            return "PARTIALLY_RESOLVED"
        return "UNRESOLVED"

    def to_dict(self) -> Dict[str, Any]:
        """Serializes to post-redistribution operational state record."""
        return {
            "phc_id": self.phc_id,
            "state_region": self.state_region,
            "district": self.district,
            "country_code": self.country_code,
            "medicine_id": self.medicine_id,
            "medicine_name": self.medicine_name,
            "original_stock": round(self.original_stock, 2),
            "incoming_units": round(self.incoming_units, 2),
            "outgoing_units": round(self.outgoing_units, 2),
            "final_stock": round(self.current_stock, 2),
            "daily_requirement": round(self.daily_requirement, 2),
            "protected_stock": round(self.protected_stock, 2),
            "remaining_requirement": round(self.required_units, 2),
            "status": self.status
        }


@dataclass
class TargetRequirement:
    """Represents a quantified shortage requirement for a target facility."""
    country_code: str
    phc_id: str
    medicine_id: str
    medicine_name: str
    district: str
    state_region: str
    initial_stock: float
    daily_forecast: float
    safety_stock: float
    planning_horizon_days: int
    target_required_units: float
    remaining_requirement: float
    is_alert_priority: bool = False
    alert_id: Optional[str] = None
    risk_level: str = "HIGH"

    @property
    def protected_target_stock(self) -> float:
        return (self.daily_forecast * self.planning_horizon_days) + self.safety_stock


@dataclass
class TransferRecord:
    """Represents a single simulated transfer between two facilities."""
    target_phc_id: str
    source_phc_id: str
    medicine_id: str
    medicine_name: str
    required_units_before_transfer: float
    source_transferable_surplus_before_transfer: float
    transferred_units: float
    distance_km: float
    remaining_target_requirement: float
    source_remaining_transferable_surplus: float
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_phc_id": self.target_phc_id,
            "source_phc_id": self.source_phc_id,
            "medicine_id": self.medicine_id,
            "medicine_name": self.medicine_name,
            "required_units_before_transfer": round(self.required_units_before_transfer, 2),
            "source_transferable_surplus_before_transfer": round(self.source_transferable_surplus_before_transfer, 2),
            "transferred_units": round(self.transferred_units, 2),
            "distance_km": round(self.distance_km, 2),
            "remaining_target_requirement": round(self.remaining_target_requirement, 2),
            "source_remaining_transferable_surplus": round(self.source_remaining_transferable_surplus, 2),
            "status": self.status
        }


@dataclass
class UnresolvedRequirement:
    """Represents a requirement that could not be fully satisfied."""
    target_phc_id: str
    medicine_id: str
    medicine_name: str
    initial_stock: float
    required_units: float
    transferred_units: float
    remaining_requirement: float
    status: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target_phc_id": self.target_phc_id,
            "medicine_id": self.medicine_id,
            "medicine_name": self.medicine_name,
            "initial_stock": round(self.initial_stock, 2),
            "required_units": round(self.required_units, 2),
            "transferred_units": round(self.transferred_units, 2),
            "remaining_requirement": round(self.remaining_requirement, 2),
            "status": self.status
        }


@dataclass
class RedistributionResult:
    """Complete output of a redistribution run."""
    country: str
    execution_timestamp: str
    total_targets_evaluated: int
    alert_priority_targets: int
    transfers_executed: List[TransferRecord] = field(default_factory=list)
    unresolved_requirements: List[UnresolvedRequirement] = field(default_factory=list)
    next_day_state: List[Dict[str, Any]] = field(default_factory=list)
    total_volume_transferred: float = 0.0
    fully_resolved_count: int = 0
    partially_resolved_count: int = 0
    unresolved_count: int = 0

    def summary_dict(self) -> Dict[str, Any]:
        return {
            "country": self.country,
            "execution_timestamp": self.execution_timestamp,
            "total_targets_evaluated": self.total_targets_evaluated,
            "alert_priority_targets": self.alert_priority_targets,
            "total_transfers_executed": len(self.transfers_executed),
            "total_volume_transferred": round(self.total_volume_transferred, 2),
            "fully_resolved_count": self.fully_resolved_count,
            "partially_resolved_count": self.partially_resolved_count,
            "unresolved_count": self.unresolved_count
        }
