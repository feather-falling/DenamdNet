"""
Prediction service for operational queries.
"""

from typing import Dict, Any, List, Optional
from ..storage.interface import StorageInterface


class PredictionService:
    def __init__(self, storage: StorageInterface):
        self.storage = storage

    def get_predictions(
        self,
        phc_id: Optional[str] = None,
        medicine_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return self.storage.get_predictions(
            phc_id=phc_id,
            medicine_id=medicine_id,
            risk_level=risk_level,
            country_code=country_code
        )
