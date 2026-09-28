"""
SQLAlchemy ORM models for BRICS Health application data:
- PHC accounts / authentication
- Medicine requests
- Request audit events / notifications
"""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class PHCAccount(Base):
    """Authenticated PHC organization account."""
    __tablename__ = "phc_accounts"

    id = Column(Integer, primary_key=True, index=True)
    phc_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    country = Column(String(100), nullable=False, default="India")
    assigned_phc_id = Column(String(100), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    requests_made = relationship("MedicineRequest", back_populates="requesting_account", foreign_keys="MedicineRequest.requesting_user_id")
    requests_supplied = relationship("MedicineRequest", back_populates="supplying_account", foreign_keys="MedicineRequest.supplied_by_user_id")


class MedicineRequest(Base):
    """Operational resource/medicine request submitted by a PHC."""
    __tablename__ = "medicine_requests"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), unique=True, index=True, nullable=False)
    
    # Requesting entity
    requesting_user_id = Column(Integer, ForeignKey("phc_accounts.id", ondelete="CASCADE"), nullable=False, index=True)
    requesting_phc_name = Column(String(255), nullable=False)
    requesting_phc_id = Column(String(100), nullable=False, index=True)
    
    # Medicine specifics
    medicine_id = Column(String(50), nullable=False, index=True)
    medicine_name = Column(String(255), nullable=False)
    quantity = Column(Float, nullable=False)
    description = Column(Text, nullable=True)
    urgency = Column(String(50), nullable=False, default="MEDIUM")
    
    # Status lifecycle: PENDING -> APPROVED -> COMPLETED | CANCELLED | REJECTED
    status = Column(String(50), nullable=False, default="PENDING", index=True)
    
    # Supplying/donor entity
    supplied_by_user_id = Column(Integer, ForeignKey("phc_accounts.id", ondelete="SET NULL"), nullable=True, index=True)
    supplied_by_phc_name = Column(String(255), nullable=True)
    supplied_by_phc_id = Column(String(100), nullable=True)
    supplied_quantity = Column(Float, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Relationships
    requesting_account = relationship("PHCAccount", back_populates="requests_made", foreign_keys=[requesting_user_id])
    supplying_account = relationship("PHCAccount", back_populates="requests_supplied", foreign_keys=[supplied_by_user_id])


class RequestEvent(Base):
    """Audit log and event notifications for requests."""
    __tablename__ = "request_events"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(String(50), index=True, nullable=False)
    actor_id = Column(Integer, nullable=True)
    actor_name = Column(String(255), nullable=False)
    action = Column(String(50), nullable=False)  # CREATED, APPROVED, COMPLETED, CANCELLED
    details = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)


Index("idx_request_status_phc", MedicineRequest.status, MedicineRequest.requesting_phc_id)
