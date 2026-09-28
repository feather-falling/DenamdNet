"""
Pydantic schemas for Redistribution execution, transfer records, and status.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class TransferSchema(BaseModel):
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


class RedistributionSummarySchema(BaseModel):
    country: str
    execution_timestamp: str
    total_targets_evaluated: int
    alert_priority_targets: int
    total_transfers_executed: int
    total_volume_transferred: float
    fully_resolved_count: int
    partially_resolved_count: int
    unresolved_count: int


class RedistributionResultsResponse(BaseModel):
    summary: RedistributionSummarySchema
    transfers: List[TransferSchema]


class RedistributionRunRequest(BaseModel):
    country: Optional[str] = "india"
    max_search_depth: Optional[int] = 4
    max_candidates_inspected: Optional[int] = 50


class RedistributionStatusResponse(BaseModel):
    status: str
    last_run_timestamp: Optional[str] = None
    summary: Optional[RedistributionSummarySchema] = None
    message: Optional[str] = None


class NextDayPHCItemSchema(BaseModel):
    phc_id: str
    state_region: str
    district: str
    country_code: str
    medicine_id: str
    medicine_name: str
    original_stock: float
    incoming_units: float
    outgoing_units: float
    final_stock: float
    daily_requirement: float
    protected_stock: float
    remaining_requirement: float
    status: str


class UnresolvedItemSchema(BaseModel):
    target_phc_id: str
    medicine_id: str
    medicine_name: str
    initial_stock: float
    required_units: float
    transferred_units: float
    remaining_requirement: float
    status: str
