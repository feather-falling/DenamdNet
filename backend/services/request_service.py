"""
Request service managing PHC operational resource requests and lifecycle transitions:
PENDING -> VISIBLE -> ACCEPTED -> TRANSFER_COORDINATED -> COMPLETED
(Also REJECTED, EXPIRED, CANCELLED)
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from ..storage.interface import StorageInterface
from ..schemas.request import RequestStatus, CreateRequestPayload


class RequestService:
    def __init__(self, storage: StorageInterface):
        self.storage = storage

    def create_request(self, payload: CreateRequestPayload) -> Dict[str, Any]:
        """Creates a new operational resource request in PENDING status."""
        now = datetime.now(timezone.utc).isoformat()
        request_id = f"REQ-{uuid.uuid4().hex[:8].upper()}"

        req_record = {
            "request_id": request_id,
            "phc_id": payload.phc_id,
            "medicine_id": payload.medicine_id,
            "quantity": payload.quantity,
            "urgency": payload.urgency.value,
            "required_by": payload.required_by,
            "reason": payload.reason,
            "status": RequestStatus.PENDING.value,
            "created_at": now,
            "updated_at": now,
            "accepted_by_phc_id": None,
            "notes": None
        }
        return self.storage.save_request(req_record)

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a single request by ID."""
        return self.storage.get_request(request_id)

    def list_requests(
        self,
        phc_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists requests filtered optionally by PHC ID and status."""
        return self.storage.list_requests(phc_id=phc_id, status=status)

    def transition_status(
        self,
        request_id: str,
        new_status: RequestStatus,
        accepted_by_phc_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Transitions request to a new status with validation."""
        req = self.storage.get_request(request_id)
        if not req:
            return None

        current_status = req.get("status")

        # Terminal status checks
        if current_status in [RequestStatus.COMPLETED.value, RequestStatus.CANCELLED.value, RequestStatus.REJECTED.value]:
            raise ValueError(f"Cannot transition request {request_id} from terminal status '{current_status}'")

        updates: Dict[str, Any] = {
            "status": new_status.value,
            "updated_at": datetime.now(timezone.utc).isoformat()
        }
        if accepted_by_phc_id:
            updates["accepted_by_phc_id"] = accepted_by_phc_id
        if notes:
            existing_notes = req.get("notes") or ""
            updates["notes"] = f"{existing_notes} [{new_status.value}]: {notes}".strip()

        return self.storage.update_request(request_id, updates)

    def accept_request(
        self,
        request_id: str,
        source_phc_id: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Accepts a request (PENDING/VISIBLE -> ACCEPTED)."""
        return self.transition_status(
            request_id=request_id,
            new_status=RequestStatus.ACCEPTED,
            accepted_by_phc_id=source_phc_id,
            notes=notes
        )

    def complete_request(
        self,
        request_id: str,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Marks request completed upon physical delivery (ACCEPTED/COORDINATED -> COMPLETED)."""
        return self.transition_status(
            request_id=request_id,
            new_status=RequestStatus.COMPLETED,
            notes=notes
        )

    def cancel_request(
        self,
        request_id: str,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Cancels an active request."""
        return self.transition_status(
            request_id=request_id,
            new_status=RequestStatus.CANCELLED,
            notes=notes
        )
