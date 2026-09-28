"""
Pydantic schemas for ML Predictions.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class ForecastDemandSchema(BaseModel):
    daily: float
    planning_horizon_days: int
    total: float


class StockoutSchema(BaseModel):
    estimated_days: float
    estimated_date: str


class RiskSchema(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    level: str = Field(..., pattern="^(LOW|MEDIUM|HIGH)$")


class AnomalySchema(BaseModel):
    score: float = Field(ge=0.0, le=1.0)
    detected: bool


class InventoryProtectionSchema(BaseModel):
    safety_stock: float
    lead_time_hours: float


class PredictionRecordSchema(BaseModel):
    timestamp: str
    phc_id: str
    country_code: str
    state_region: str
    district: str
    medicine_id: str
    medicine_name: str
    unit: str
    current_stock: float
    forecast_demand: ForecastDemandSchema
    stockout: StockoutSchema
    risk: RiskSchema
    anomaly: AnomalySchema
    inventory_protection: InventoryProtectionSchema


class PredictionQueryResponse(BaseModel):
    total_records: int
    filtered_records: int
    records: List[PredictionRecordSchema]
