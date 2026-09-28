"""
Redistribution API endpoints.
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from ..schemas.redistribution import (
    RedistributionRunRequest,
    RedistributionStatusResponse,
    RedistributionResultsResponse
)
from ..services.redistribution_service import RedistributionService
from ..storage.json_store import JsonStorage

router = APIRouter(prefix="/api/redistribution", tags=["Redistribution"])


def get_redistribution_service() -> RedistributionService:
    return RedistributionService(JsonStorage())


@router.post("/run", response_model=Dict[str, Any])
def run_redistribution(
    payload: Optional[RedistributionRunRequest] = None,
    service: RedistributionService = Depends(get_redistribution_service)
) -> Dict[str, Any]:
    """Triggers the Redistribution Engine on the latest ML outputs."""
    country = payload.country if payload else "india"
    max_depth = payload.max_search_depth if payload and payload.max_search_depth is not None else 4
    max_cands = payload.max_candidates_inspected if payload and payload.max_candidates_inspected is not None else 50

    try:
        result = service.run_redistribution(
            country=country,
            max_search_depth=max_depth,
            max_candidates_inspected=max_cands
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Redistribution execution failed: {str(e)}"
        )


@router.get("/status", response_model=RedistributionStatusResponse)
def get_redistribution_status(
    service: RedistributionService = Depends(get_redistribution_service)
) -> RedistributionStatusResponse:
    """Returns current status and execution timestamp of the redistribution engine."""
    stat = service.get_status()
    return RedistributionStatusResponse(**stat)


@router.get("/results", response_model=RedistributionResultsResponse)
def get_redistribution_results(
    service: RedistributionService = Depends(get_redistribution_service)
) -> RedistributionResultsResponse:
    """Returns detailed transfer records and execution summary from the latest run."""
    results = service.get_results()
    if not results:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No redistribution results found. Run redistribution first."
        )
    return RedistributionResultsResponse(**results)
