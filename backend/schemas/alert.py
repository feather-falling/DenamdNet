"""
Pydantic schemas for Disease Outbreak Alerts.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class AlertRecordSchema(BaseModel):
    alert_id: str
    timestamp: str
    country_code: str
    phc_id: str
    district: str
    pattern_type: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    severity: str = Field(..., pattern="^(WATCH|WARNING|EMERGENCY)$")
    correlated_resources: List[str]
    primary_driver: str
    spatial_cluster_size: int = Field(ge=1)
    recommended_actions: List[str]


class AlertQueryResponse(BaseModel):
    total_alerts: int
    filtered_alerts: int
    alerts: List[AlertRecordSchema]
