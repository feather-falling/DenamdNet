"""
Authentication endpoints for PHC accounts:
- Register
- Login
- Current User Profile
- Logout
"""

import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..db.database import get_db
from ..db.models import PHCAccount
from ..schemas.auth import RegisterRequest, LoginRequest, AuthResponse, PHCUserResponse
from ..auth.security import hash_password, verify_password, create_access_token
from ..auth.deps import get_current_user

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Registers a new PHC organization account with a securely hashed password."""
    # Check if email is already taken
    existing = db.query(PHCAccount).filter(PHCAccount.email == payload.email.lower()).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address is already registered."
        )

    # Hash password securely with bcrypt
    hashed = hash_password(payload.password)

    # Generate a readable assigned PHC identifier for human coordination
    country_prefix = "IN"
    if payload.country:
        c_lower = payload.country.lower()
        if "brazil" in c_lower:
            country_prefix = "BR"
        elif "south" in c_lower or "africa" in c_lower:
            country_prefix = "ZA"
    assigned_phc_id = f"{country_prefix}-PORTAL-{uuid.uuid4().hex[:6].upper()}"

    new_user = PHCAccount(
        phc_name=payload.phc_name.strip(),
        email=payload.email.lower().strip(),
        password_hash=hashed,
        country=payload.country or "India",
        assigned_phc_id=assigned_phc_id
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    # Create JWT access token
    token = create_access_token({"sub": str(new_user.id), "email": new_user.email})

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=PHCUserResponse.model_validate(new_user)
    )


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    """Authenticates a PHC account via email & password and returns a JWT access token."""
    user = db.query(PHCAccount).filter(PHCAccount.email == payload.email.lower().strip()).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    token = create_access_token({"sub": str(user.id), "email": user.email})

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        user=PHCUserResponse.model_validate(user)
    )


@router.get("/me", response_model=PHCUserResponse)
def get_me(current_user: PHCAccount = Depends(get_current_user)) -> PHCUserResponse:
    """Returns the authenticated PHC account profile."""
    return PHCUserResponse.model_validate(current_user)


@router.post("/logout")
def logout() -> dict:
    """Client logout confirmation endpoint."""
    return {"status": "SUCCESS", "message": "Successfully logged out."}
