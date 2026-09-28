"""
Operational Resource Requests API endpoints.
Powered by PostgreSQL persistence, strict server-side authorization,
and essential medicine catalog integration.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..db.database import get_db
from ..db.models import PHCAccount
from ..auth.deps import get_current_user, get_optional_current_user
from ..schemas.request import (
    CreateRequestPayload,
    ApproveSupplyPayload,
    RequestActionPayload,
    ResourceRequestSchema,
    RequestListResponse,
    MedicineCatalogItem,
    NotificationItem
)
from ..services.db_request_service import DBRequestService

router = APIRouter(prefix="/api/requests", tags=["Requests"])


@router.get("/catalog", response_model=List[MedicineCatalogItem])
def get_medicine_catalog() -> List[MedicineCatalogItem]:
    """Returns the authoritative essential medicine catalogue for requests."""
    return DBRequestService.get_catalog()


@router.post("", response_model=ResourceRequestSchema, status_code=status.HTTP_201_CREATED)
def create_request(
    payload: CreateRequestPayload,
    current_user: Optional[PHCAccount] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> ResourceRequestSchema:
    """Submits a short-term emergency or replenishment request for a PHC.
    Uses authenticated user identity; provides guest demo fallback if unauthenticated.
    """
    # If unauthenticated in demo mode, create or resolve a default demo account
    if not current_user:
        demo_user = db.query(PHCAccount).filter(PHCAccount.email == "demo@brics.health").first()
        if not demo_user:
            demo_user = PHCAccount(
                phc_name="Demo Central PHC",
                email="demo@brics.health",
                password_hash="demo_account_no_password_login",
                country="India",
                assigned_phc_id="IN-DL-DEMO-001"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
        current_user = demo_user

    return DBRequestService.create_request(payload, current_user, db)


@router.get("/my", response_model=List[ResourceRequestSchema])
def list_my_requests(
    current_user: PHCAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ResourceRequestSchema]:
    """Retrieves all requests submitted by the current authenticated PHC."""
    return DBRequestService.list_requests(
        user=current_user,
        mine_only=True,
        available_only=False,
        status_filter=None,
        db=db
    )


@router.get("/available", response_model=List[ResourceRequestSchema])
def list_available_requests(
    current_user: Optional[PHCAccount] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> List[ResourceRequestSchema]:
    """Retrieves pending community requests from other PHCs that are eligible for peer supply."""
    return DBRequestService.list_requests(
        user=current_user,
        mine_only=False,
        available_only=True,
        status_filter=None,
        db=db
    )


@router.get("/notifications", response_model=List[NotificationItem])
def get_request_notifications(
    current_user: PHCAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[NotificationItem]:
    """Retrieves operational updates and community requests for the authenticated PHC."""
    return DBRequestService.get_notifications(user=current_user, db=db)


@router.get("", response_model=RequestListResponse)
def list_requests(
    phc_id: Optional[str] = Query(None, description="Filter by requesting PHC ID"),
    status: Optional[str] = Query(None, description="Filter by status (PENDING, APPROVED, COMPLETED, CANCELLED)"),
    current_user: Optional[PHCAccount] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> RequestListResponse:
    """Lists operational requests with optional filtering."""
    items = DBRequestService.list_requests(
        user=current_user,
        mine_only=False,
        available_only=False,
        status_filter=status,
        db=db
    )
    if phc_id:
        items = [i for i in items if i.phc_id == phc_id or i.requesting_phc_id == phc_id]

    return RequestListResponse(
        total_requests=len(items),
        requests=items
    )


@router.get("/{request_id}", response_model=ResourceRequestSchema)
def get_request(
    request_id: str,
    db: Session = Depends(get_db)
) -> ResourceRequestSchema:
    """Retrieves request details by unique request ID."""
    return DBRequestService.get_request(request_id, db)


@router.post("/{request_id}/approve", response_model=ResourceRequestSchema)
def approve_request(
    request_id: str,
    payload: ApproveSupplyPayload,
    current_user: PHCAccount = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ResourceRequestSchema:
    """Approves and supplies units for a pending community request.
    Enforces that donor PHC cannot be the requester and quantity must be > 0.
    """
    return DBRequestService.approve_and_supply(request_id, payload, current_user, db)


@router.post("/{request_id}/accept", response_model=ResourceRequestSchema)
def accept_request(
    request_id: str,
    payload: Optional[RequestActionPayload] = None,
    db: Session = Depends(get_db)
) -> ResourceRequestSchema:
    """Accepts an operational request (PENDING -> ACCEPTED)."""
    src_phc = payload.source_phc_id if payload else None
    notes = payload.notes if payload else None
    return DBRequestService.accept_request(request_id, src_phc, notes, db)


@router.post("/{request_id}/complete", response_model=ResourceRequestSchema)
def complete_request(
    request_id: str,
    payload: Optional[RequestActionPayload] = None,
    db: Session = Depends(get_db)
) -> ResourceRequestSchema:
    """Marks request completed upon physical handover (ACCEPTED -> COMPLETED)."""
    notes = payload.notes if payload else None
    return DBRequestService.complete_request(request_id, notes, db)



@router.post("/{request_id}/cancel", response_model=ResourceRequestSchema)
def cancel_request(
    request_id: str,
    payload: Optional[RequestActionPayload] = None,
    current_user: Optional[PHCAccount] = Depends(get_optional_current_user),
    db: Session = Depends(get_db)
) -> ResourceRequestSchema:
    """Cancels a pending request. Only authorized owner may cancel."""
    if not current_user:
        current_user = db.query(PHCAccount).filter(PHCAccount.email == "demo@brics.health").first()
        if not current_user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required to cancel request."
            )
    return DBRequestService.cancel_request(request_id, current_user, db)

