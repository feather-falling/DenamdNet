"""
Pydantic schemas for PHC Operational Resource Requests and Community Portal.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ConfigDict


class RequestStatus(str, Enum):
    PENDING = "PENDING"
    VISIBLE = "VISIBLE"
    ACCEPTED = "ACCEPTED"
    APPROVED = "APPROVED"
    TRANSFER_COORDINATED = "TRANSFER_COORDINATED"
    COMPLETED = "COMPLETED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class RequestUrgency(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CreateRequestPayload(BaseModel):
    """Payload for submitting a request."""
    medicine_id: str = Field(..., min_length=1, description="Requested Medicine ID from catalog")
    medicine_name: Optional[str] = Field(None, description="Optional medicine name")
    quantity: float = Field(..., gt=0, description="Requested quantity in units (must be > 0)")
    urgency: RequestUrgency = Field(default=RequestUrgency.MEDIUM, description="Urgency level")
    reason: Optional[str] = Field(None, description="Clinical or operational justification")
    description: Optional[str] = Field(None, description="Detailed requirement notes")
    required_by: Optional[str] = Field(None, description="Target date needed")
    phc_id: Optional[str] = Field(None, description="Optional override, default taken from authenticated user")


class ApproveSupplyPayload(BaseModel):
    """Payload when a donor PHC approves and supplies medicine units."""
    units_to_send: float = Field(..., gt=0, description="Quantity of units to supply (> 0)")
    notes: Optional[str] = Field(None, max_length=500, description="Coordination or batch notes")


class RequestActionPayload(BaseModel):
    source_phc_id: Optional[str] = None
    units_to_send: Optional[float] = None
    notes: Optional[str] = None


class ResourceRequestSchema(BaseModel):
    id: Optional[int] = None
    request_id: str
    phc_id: str
    requesting_phc_name: Optional[str] = None
    requesting_phc_id: Optional[str] = None
    medicine_id: str
    medicine_name: Optional[str] = None
    quantity: float
    urgency: str = "MEDIUM"
    required_by: Optional[str] = None
    reason: Optional[str] = None
    description: Optional[str] = None
    status: str
    supplied_by_phc_name: Optional[str] = None
    supplied_by_phc_id: Optional[str] = None
    supplied_quantity: Optional[float] = None
    accepted_by_phc_id: Optional[str] = None
    notes: Optional[str] = None
    created_at: str
    updated_at: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)



class RequestListResponse(BaseModel):
    total_requests: int
    requests: List[ResourceRequestSchema]


class MedicineCatalogItem(BaseModel):
    medicine_id: str
    name: str
    unit: str
    category: str


class NotificationItem(BaseModel):
    id: str
    request_id: str
    title: str
    message: str
    type: str  # info, success, warning
    timestamp: str
    status: str
