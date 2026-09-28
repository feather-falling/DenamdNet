"""
Pydantic schemas for PHC facility metadata and inventory views.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel


class PHCGeographySchema(BaseModel):
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PHCCapacitySchema(BaseModel):
    beds: Optional[int] = None
    opd_capacity_per_day: Optional[int] = None
    emergency_beds: Optional[int] = None


class PHCStaffingSchema(BaseModel):
    doctors: Optional[int] = None
    nurses: Optional[int] = None
    pharmacists: Optional[int] = None


class PHCDetailSchema(BaseModel):
    phc_id: str
    name: str
    country: str
    state: Optional[str] = None
    district: Optional[str] = None
    city: Optional[str] = None
    locality: Optional[str] = None
    facility_type: Optional[str] = None
    geography: Optional[PHCGeographySchema] = None
    capacity: Optional[PHCCapacitySchema] = None
    staffing_baseline: Optional[PHCStaffingSchema] = None


class PHCInventoryItemSchema(BaseModel):
    medicine_id: str
    medicine_name: str
    unit: Optional[str] = "units"
    current_stock: float
    daily_requirement: float
    safety_stock: float
    protected_stock: float
    transferable_surplus: float
    remaining_requirement: float
    status: str


class PHCInventoryResponse(BaseModel):
    phc_id: str
    phc_name: str
    district: str
    state: str
    inventory: List[PHCInventoryItemSchema]
