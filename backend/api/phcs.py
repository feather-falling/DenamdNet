"""
PHC API endpoints for facility metadata and inventory.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from ..schemas.phc import PHCDetailSchema, PHCInventoryResponse
from ..services.phc_service import PHCService
from ..storage.json_store import JsonStorage

router = APIRouter(prefix="/api/phcs", tags=["PHCs"])


def get_phc_service() -> PHCService:
    return PHCService(JsonStorage())


@router.get("", response_model=List[Dict[str, Any]])
def list_phcs(
    country: Optional[str] = Query(None, description="Filter PHCs by country"),
    service: PHCService = Depends(get_phc_service)
) -> List[Dict[str, Any]]:
    """Lists healthcare facilities."""
    return service.list_phcs(country=country)


@router.get("/{phc_id}", response_model=Dict[str, Any])
def get_phc(
    phc_id: str,
    service: PHCService = Depends(get_phc_service)
) -> Dict[str, Any]:
    """Retrieves facility master record."""
    phc = service.get_phc(phc_id)
    if not phc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PHC '{phc_id}' not found."
        )
    return phc


@router.get("/{phc_id}/inventory", response_model=PHCInventoryResponse)
def get_phc_inventory(
    phc_id: str,
    service: PHCService = Depends(get_phc_service)
) -> PHCInventoryResponse:
    """Retrieves current and post-redistribution operational inventory for a PHC."""
    inv = service.get_phc_inventory(phc_id)
    if not inv:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"PHC '{phc_id}' not found or inventory unavailable."
        )
    return PHCInventoryResponse(**inv)
