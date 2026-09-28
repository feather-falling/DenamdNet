"""
Results Dashboard API Endpoints.
Exposes actual generated results from the daily pipeline:
- Summary KPI statistics
- Transfer details with donor/recipient traceability
- Country-level analytics
- Medicine-level movement & ranking
- Post-redistribution inventory (HEALTHY vs RESOLVED)
- Direct output file downloads
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import FileResponse
from ..services.pipeline_orchestrator import orchestrator, PROJECT_ROOT, OUTPUT_DIR

router = APIRouter(prefix="/api/results", tags=["Results Dashboard"])


@router.get("/summary")
def get_results_summary() -> Dict[str, Any]:
    """Returns top-level KPIs, resolution counts, and country metrics computed from actual generated results."""
    return orchestrator.calculate_summary_statistics()


@router.get("/transfers")
def get_transfers(
    search: Optional[str] = Query(None, description="Search by PHC ID or medicine name"),
    medicine_id: Optional[str] = Query(None, description="Filter by medicine ID"),
    country_code: Optional[str] = Query(None, description="Filter by country code (IN, BR, ZA)"),
    status: Optional[str] = Query(None, description="Filter by status (RESOLVED, PARTIALLY_RESOLVED)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """Returns paginated transfer records showing who donated, who received, and quantities moved."""
    return orchestrator.get_transfers(
        search=search,
        medicine_id=medicine_id,
        country_code=country_code,
        status_filter=status,
        limit=limit,
        offset=offset
    )


@router.get("/medicines")
def get_medicine_movements() -> List[Dict[str, Any]]:
    """Returns medicine-level transfer volumes and resolution statistics."""
    return orchestrator.get_medicine_movements()


@router.get("/inventory")
def get_next_day_inventory(
    phc_id: Optional[str] = Query(None, description="Filter by PHC ID"),
    country_code: Optional[str] = Query(None, description="Filter by country code (IN, BR, ZA)"),
    status: Optional[str] = Query(None, description="Filter by status (HEALTHY, RESOLVED, PARTIALLY_RESOLVED, UNRESOLVED)"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0)
) -> Dict[str, Any]:
    """Returns next-day inventory outcomes (HEALTHY vs RESOLVED)."""
    return orchestrator.get_next_day_inventory(
        phc_id=phc_id,
        country_code=country_code,
        status_filter=status,
        limit=limit,
        offset=offset
    )


# ─────────────────────────────────────────────
# File Downloads
# ─────────────────────────────────────────────

@router.get("/download/next-day-phc-data")
def download_next_day_phc_data():
    """Downloads the generated next_day_phc_data.json."""
    filepath = os.path.join(OUTPUT_DIR, "next_day_phc_data.json")
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File next_day_phc_data.json not found. Run pipeline first."
        )
    return FileResponse(
        path=filepath,
        filename="next_day_phc_data.json",
        media_type="application/json"
    )


@router.get("/download/redistribution-results")
def download_redistribution_results():
    """Downloads the generated redistribution_results.json."""
    filepath = os.path.join(OUTPUT_DIR, "redistribution_results.json")
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File redistribution_results.json not found. Run pipeline first."
        )
    return FileResponse(
        path=filepath,
        filename="redistribution_results.json",
        media_type="application/json"
    )


@router.get("/download/unresolved-requirements")
def download_unresolved_requirements():
    """Downloads the generated unresolved_requirements.json."""
    filepath = os.path.join(OUTPUT_DIR, "unresolved_requirements.json")
    if not os.path.exists(filepath):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File unresolved_requirements.json not found. Run pipeline first."
        )
    return FileResponse(
        path=filepath,
        filename="unresolved_requirements.json",
        media_type="application/json"
    )
