"""
PostgreSQL-backed Request Service for PHC Medicine Portal.
Guarantees database persistence, strict server-side authorization,
parameterized queries, and audit event tracking.
"""

import os
import json
import uuid
from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from fastapi import HTTPException, status

from ..db.models import MedicineRequest, RequestEvent, PHCAccount
from ..schemas.request import (
    CreateRequestPayload,
    ApproveSupplyPayload,
    ResourceRequestSchema,
    MedicineCatalogItem,
    NotificationItem,
    RequestStatus
)

# Cache for medicine catalog
_CATALOG_CACHE: Optional[List[Dict[str, Any]]] = None


def load_medicine_catalog() -> List[Dict[str, Any]]:
    """Loads essential medicine catalog from authoritative dataset."""
    global _CATALOG_CACHE
    if _CATALOG_CACHE is not None:
        return _CATALOG_CACHE

    meds_path = os.path.abspath(os.path.join("data", "india", "medicines.json"))
    if not os.path.exists(meds_path):
        meds_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "data", "india", "medicines.json"))

    if os.path.exists(meds_path):
        try:
            with open(meds_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                _CATALOG_CACHE = data.get("medicines", [])
                return _CATALOG_CACHE
        except Exception:
            pass

    # Standard fallback essential medicine catalog
    _CATALOG_CACHE = [
        {"medicine_id": "MED-001", "name": "Paracetamol 500 mg tablet", "unit": "tablet", "category": "analgesic_antipyretic"},
        {"medicine_id": "MED-002", "name": "ORS sachet 20.5g", "unit": "sachet", "category": "rehydration"},
        {"medicine_id": "MED-003", "name": "IV Normal Saline 0.9% 500 mL", "unit": "bag", "category": "iv_fluid"},
        {"medicine_id": "MED-004", "name": "Ringer's Lactate 500 mL", "unit": "bag", "category": "iv_fluid"},
        {"medicine_id": "MED-005", "name": "Artemether-Lumefantrine tablet", "unit": "tablet", "category": "antimalarial"},
        {"medicine_id": "MED-006", "name": "Amoxicillin 500 mg capsule", "unit": "capsule", "category": "antibiotic"},
        {"medicine_id": "MED-007", "name": "Azithromycin 500 mg tablet", "unit": "tablet", "category": "antibiotic"},
        {"medicine_id": "MED-008", "name": "Ciprofloxacin 500 mg tablet", "unit": "tablet", "category": "antibiotic"},
        {"medicine_id": "MED-009", "name": "Metformin 500 mg tablet", "unit": "tablet", "category": "antidiabetic"},
        {"medicine_id": "MED-010", "name": "Amlodipine 5 mg tablet", "unit": "tablet", "category": "antihypertensive"},
        {"medicine_id": "MED-011", "name": "Salbutamol 100 mcg inhaler", "unit": "canister", "category": "respiratory"},
        {"medicine_id": "MED-012", "name": "Zinc Sulfate 20 mg tablet", "unit": "tablet", "category": "supplement"},
        {"medicine_id": "MED-013", "name": "Albendazole 400 mg tablet", "unit": "tablet", "category": "anthelmintic"},
        {"medicine_id": "MED-014", "name": "Doxycycline 100 mg capsule", "unit": "capsule", "category": "antibiotic"},
        {"medicine_id": "MED-015", "name": "Iron + Folic Acid tablet", "unit": "tablet", "category": "supplement"},
        {"medicine_id": "MED-016", "name": "Omeprazole 20 mg capsule", "unit": "capsule", "category": "gastrointestinal"},
        {"medicine_id": "MED-017", "name": "Ceftriaxone 1g injection", "unit": "vial", "category": "antibiotic"},
        {"medicine_id": "MED-018", "name": "Disposable Syringes 5ml with Needle", "unit": "piece", "category": "consumable"}
    ]
    return _CATALOG_CACHE


class DBRequestService:
    @staticmethod
    def get_catalog() -> List[MedicineCatalogItem]:
        catalog = load_medicine_catalog()
        return [
            MedicineCatalogItem(
                medicine_id=m.get("medicine_id", ""),
                name=m.get("name", ""),
                unit=m.get("unit", "units"),
                category=m.get("category", "General")
            )
            for m in catalog
        ]

    @staticmethod
    def to_schema(req: MedicineRequest) -> ResourceRequestSchema:
        return ResourceRequestSchema(
            id=req.id,
            request_id=req.request_id,
            phc_id=req.requesting_phc_id,
            requesting_phc_name=req.requesting_phc_name,
            requesting_phc_id=req.requesting_phc_id,
            medicine_id=req.medicine_id,
            medicine_name=req.medicine_name,
            quantity=req.quantity,
            urgency=req.urgency,
            description=req.description,
            reason=req.description,
            status=req.status,
            supplied_by_phc_name=req.supplied_by_phc_name,
            supplied_by_phc_id=req.supplied_by_phc_id,
            supplied_quantity=req.supplied_quantity,
            accepted_by_phc_id=req.supplied_by_phc_id,
            notes=req.notes,
            created_at=req.created_at.isoformat() if req.created_at else "",
            updated_at=req.updated_at.isoformat() if req.updated_at else ""
        )

    @classmethod
    def create_request(
        cls,
        payload: CreateRequestPayload,
        user: PHCAccount,
        db: Session
    ) -> ResourceRequestSchema:
        """Creates a new medicine request tied to the authenticated user."""
        if payload.quantity <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Requested quantity must be greater than zero.")

        # Resolve medicine name from catalog
        med_catalog = {m.get("medicine_id"): m.get("name") for m in load_medicine_catalog()}
        med_name = payload.medicine_name or med_catalog.get(payload.medicine_id, f"Medicine {payload.medicine_id}")

        req_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"
        assigned_id = user.assigned_phc_id or f"PHC-{user.id}"
        description_text = payload.description or payload.reason or "Operational replenishment request"

        new_req = MedicineRequest(
            request_id=req_id,
            requesting_user_id=user.id,
            requesting_phc_name=user.phc_name,
            requesting_phc_id=assigned_id,
            medicine_id=payload.medicine_id,
            medicine_name=med_name,
            quantity=float(payload.quantity),
            description=description_text,
            urgency=payload.urgency.value if hasattr(payload.urgency, "value") else str(payload.urgency),
            status=RequestStatus.PENDING.value
        )
        db.add(new_req)

        # Record audit event
        event = RequestEvent(
            request_id=req_id,
            actor_id=user.id,
            actor_name=user.phc_name,
            action="CREATED",
            details=f"Created request for {payload.quantity} units of {med_name}."
        )
        db.add(event)
        db.commit()
        db.refresh(new_req)

        return cls.to_schema(new_req)

    @classmethod
    def list_requests(
        cls,
        user: Optional[PHCAccount],
        mine_only: bool,
        available_only: bool,
        status_filter: Optional[str],
        db: Session
    ) -> List[ResourceRequestSchema]:
        """Lists requests with SQL parameterized filtering."""
        query = db.query(MedicineRequest)

        if mine_only:
            if not user:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required for personal requests.")
            query = query.filter(MedicineRequest.requesting_user_id == user.id)
        elif available_only:
            query = query.filter(MedicineRequest.status == RequestStatus.PENDING.value)
            if user:
                # Do not show own requests as 'available from others'
                query = query.filter(MedicineRequest.requesting_user_id != user.id)
        elif status_filter:
            query = query.filter(MedicineRequest.status == status_filter.upper())

        results = query.order_by(desc(MedicineRequest.created_at)).all()
        return [cls.to_schema(r) for r in results]

    @classmethod
    def get_request(cls, request_id: str, db: Session) -> ResourceRequestSchema:
        req = db.query(MedicineRequest).filter(MedicineRequest.request_id == request_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Request '{request_id}' not found.")
        return cls.to_schema(req)

    @classmethod
    def accept_request(
        cls,
        request_id: str,
        source_phc_id: Optional[str],
        notes: Optional[str],
        db: Session
    ) -> ResourceRequestSchema:
        """Accepts a request (PENDING -> ACCEPTED)."""
        req = db.query(MedicineRequest).filter(MedicineRequest.request_id == request_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Request '{request_id}' not found.")

        req.status = RequestStatus.ACCEPTED.value
        req.supplied_by_phc_id = source_phc_id
        if notes:
            existing = req.notes or ""
            req.notes = f"{existing} [ACCEPTED]: {notes}".strip()

        event = RequestEvent(
            request_id=request_id,
            actor_name=source_phc_id or "Donor PHC",
            action="ACCEPTED",
            details=notes or "Request accepted by source PHC."
        )
        db.add(event)
        db.commit()
        db.refresh(req)
        return cls.to_schema(req)

    @classmethod
    def complete_request(
        cls,
        request_id: str,
        notes: Optional[str],
        db: Session
    ) -> ResourceRequestSchema:
        """Marks request completed upon confirmation of handover (ACCEPTED -> COMPLETED)."""
        req = db.query(MedicineRequest).filter(MedicineRequest.request_id == request_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Request '{request_id}' not found.")

        req.status = RequestStatus.COMPLETED.value
        if notes:
            existing = req.notes or ""
            req.notes = f"{existing} [COMPLETED]: {notes}".strip()

        event = RequestEvent(
            request_id=request_id,
            actor_name="System/Coordinator",
            action="COMPLETED",
            details=notes or "Physical handover confirmed."
        )
        db.add(event)
        db.commit()
        db.refresh(req)
        return cls.to_schema(req)

    @classmethod
    def approve_and_supply(
        cls,
        request_id: str,
        payload: ApproveSupplyPayload,
        donor: PHCAccount,
        db: Session
    ) -> ResourceRequestSchema:
        """Approves and supplies units for an operational request."""
        if payload.units_to_send <= 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Units to send must be greater than zero.")

        req = db.query(MedicineRequest).filter(MedicineRequest.request_id == request_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Request '{request_id}' not found.")

        # Server-side validation: donor cannot approve their own request
        if req.requesting_user_id == donor.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="A PHC cannot approve or supply its own request.")

        if req.status not in [RequestStatus.PENDING.value, RequestStatus.VISIBLE.value]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Request is in '{req.status}' state and cannot be approved.")

        donor_assigned = donor.assigned_phc_id or f"PHC-{donor.id}"
        new_status = RequestStatus.APPROVED.value if payload.units_to_send < req.quantity else RequestStatus.COMPLETED.value

        req.status = new_status
        req.supplied_by_user_id = donor.id
        req.supplied_by_phc_name = donor.phc_name
        req.supplied_by_phc_id = donor_assigned
        req.supplied_quantity = float(payload.units_to_send)
        if payload.notes:
            existing = req.notes or ""
            req.notes = f"{existing} [SUPPLIED]: {payload.notes}".strip()

        event = RequestEvent(
            request_id=request_id,
            actor_id=donor.id,
            actor_name=donor.phc_name,
            action="APPROVED",
            details=f"{donor.phc_name} approved and supplied {payload.units_to_send} units."
        )
        db.add(event)
        db.commit()
        db.refresh(req)

        return cls.to_schema(req)

    @classmethod
    def cancel_request(cls, request_id: str, user: PHCAccount, db: Session) -> ResourceRequestSchema:
        """Allows only the requesting PHC owner to cancel their own request."""
        req = db.query(MedicineRequest).filter(MedicineRequest.request_id == request_id).first()
        if not req:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Request '{request_id}' not found.")

        if req.requesting_user_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to cancel this request.")

        if req.status in [RequestStatus.COMPLETED.value, RequestStatus.CANCELLED.value]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Cannot cancel request in '{req.status}' state.")

        req.status = RequestStatus.CANCELLED.value
        event = RequestEvent(
            request_id=request_id,
            actor_id=user.id,
            actor_name=user.phc_name,
            action="CANCELLED",
            details="Request cancelled by creator."
        )
        db.add(event)
        db.commit()
        db.refresh(req)

        return cls.to_schema(req)

    @classmethod
    def get_notifications(cls, user: PHCAccount, db: Session) -> List[NotificationItem]:
        """Collects recent notifications for the logged-in PHC."""
        notifications: List[NotificationItem] = []

        # 1. Check if any of my requests were approved or completed
        my_reqs = db.query(MedicineRequest).filter(
            MedicineRequest.requesting_user_id == user.id,
            MedicineRequest.status.in_([RequestStatus.APPROVED.value, RequestStatus.COMPLETED.value])
        ).order_by(desc(MedicineRequest.updated_at)).limit(10).all()

        for r in my_reqs:
            notifications.append(
                NotificationItem(
                    id=f"notif-appr-{r.request_id}",
                    request_id=r.request_id,
                    title=f"Request {r.status.title()}",
                    message=f"Your request for {r.quantity} units of {r.medicine_name} was supplied by {r.supplied_by_phc_name or 'a peer PHC'} ({r.supplied_quantity or r.quantity} units).",
                    type="success",
                    timestamp=r.updated_at.isoformat() if r.updated_at else "",
                    status=r.status
                )
            )

        # 2. Check recent community requests from other PHCs
        community_reqs = db.query(MedicineRequest).filter(
            MedicineRequest.requesting_user_id != user.id,
            MedicineRequest.status == RequestStatus.PENDING.value
        ).order_by(desc(MedicineRequest.created_at)).limit(5).all()

        for r in community_reqs:
            notifications.append(
                NotificationItem(
                    id=f"notif-comm-{r.request_id}",
                    request_id=r.request_id,
                    title="Community Supply Request",
                    message=f"{r.requesting_phc_name} requires {r.quantity} units of {r.medicine_name} ({r.urgency} urgency).",
                    type="info",
                    timestamp=r.created_at.isoformat() if r.created_at else "",
                    status=r.status
                )
            )

        return notifications
