"""
Alert service for querying and filtering disease outbreak early warnings.
"""

from typing import Dict, Any, List, Optional
from ..storage.interface import StorageInterface


class AlertService:
    def __init__(self, storage: StorageInterface):
        self.storage = storage

    def get_alerts(
        self,
        phc_id: Optional[str] = None,
        district: Optional[str] = None,
        severity: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        return self.storage.get_alerts(
            phc_id=phc_id,
            district=district,
            severity=severity,
            country_code=country_code
        )
