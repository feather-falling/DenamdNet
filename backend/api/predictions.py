"""
Prediction API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ..schemas.prediction import PredictionQueryResponse, PredictionRecordSchema
from ..services.prediction_service import PredictionService
from ..storage.json_store import JsonStorage

router = APIRouter(prefix="/api/predictions", tags=["Predictions"])


def get_prediction_service() -> PredictionService:
    return PredictionService(JsonStorage())


@router.get("", response_model=PredictionQueryResponse)
def get_predictions(
    phc_id: Optional[str] = Query(None, description="Filter by PHC ID"),
    medicine_id: Optional[str] = Query(None, description="Filter by Medicine ID"),
    risk_level: Optional[str] = Query(None, description="Filter by Risk Level (LOW, MEDIUM, HIGH)"),
    country_code: Optional[str] = Query(None, description="Filter by ISO Country Code (e.g. IN, BR, ZA)"),
    service: PredictionService = Depends(get_prediction_service)
) -> PredictionQueryResponse:
    """Queries Sharma redistribution forecast and risk predictions."""
    records = service.get_predictions(
        phc_id=phc_id,
        medicine_id=medicine_id,
        risk_level=risk_level,
        country_code=country_code
    )
    return PredictionQueryResponse(
        total_records=len(records),
        filtered_records=len(records),
        records=records
    )
