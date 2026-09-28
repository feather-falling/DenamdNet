"""
Health check endpoint.
"""

from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=Dict[str, Any])
def health_check() -> Dict[str, Any]:
    """Returns operational health status of the backend."""
    return {
        "status": "healthy",
        "service": "brics-smart-health-resilience",
        "version": "1.0.0"
    }
