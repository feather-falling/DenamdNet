"""
Alerts API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from ..schemas.alert import AlertQueryResponse, AlertRecordSchema
from ..services.alert_service import AlertService
from ..storage.json_store import JsonStorage

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


def get_alert_service() -> AlertService:
    return AlertService(JsonStorage())


@router.get("", response_model=AlertQueryResponse)
def get_alerts(
    phc_id: Optional[str] = Query(None, description="Filter by PHC ID"),
    district: Optional[str] = Query(None, description="Filter by District"),
    severity: Optional[str] = Query(None, description="Filter by Severity (WATCH, WARNING, EMERGENCY)"),
    country_code: Optional[str] = Query(None, description="Filter by Country Code (IN, BR, ZA)"),
    service: AlertService = Depends(get_alert_service)
) -> AlertQueryResponse:
    """Queries early warning outbreak and anomaly alerts."""
    alerts = service.get_alerts(
        phc_id=phc_id,
        district=district,
        severity=severity,
        country_code=country_code
    )
    return AlertQueryResponse(
        total_alerts=len(alerts),
        filtered_alerts=len(alerts),
        alerts=alerts
    )
