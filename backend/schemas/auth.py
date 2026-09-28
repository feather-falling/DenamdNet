"""
Pydantic schemas for authentication and PHC user accounts.
"""

import re
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict


class RegisterRequest(BaseModel):
    phc_name: str = Field(..., min_length=2, max_length=200, description="PHC or healthcare organization name")
    email: str = Field(..., description="Valid work/institutional email address")
    password: str = Field(..., min_length=6, max_length=128, description="Secure password")
    country: Optional[str] = Field("India", description="Country of operation")

    @field_validator("email")
    def validate_email_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format.")
        return v


class LoginRequest(BaseModel):
    email: str = Field(..., description="Registered email address")
    password: str = Field(..., description="Account password")

    @field_validator("email")
    def validate_email_format(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@]+@[^@]+\.[^@]+$", v):
            raise ValueError("Invalid email format.")
        return v


class PHCUserResponse(BaseModel):
    id: int
    phc_name: str
    email: str
    country: str
    assigned_phc_id: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)



class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: PHCUserResponse
