"""
PHC Service for facility metadata and inventory lookup.
"""

from typing import Dict, Any, List, Optional
from ..storage.interface import StorageInterface


class PHCService:
    def __init__(self, storage: StorageInterface):
        self.storage = storage

    def get_phc(self, phc_id: str) -> Optional[Dict[str, Any]]:
        return self.storage.get_phc(phc_id)

    def list_phcs(self, country: Optional[str] = None) -> List[Dict[str, Any]]:
        return self.storage.list_phcs(country=country)

    def get_phc_inventory(self, phc_id: str) -> Optional[Dict[str, Any]]:
        phc = self.storage.get_phc(phc_id)
        if not phc:
            return None
        inventory = self.storage.get_phc_inventory(phc_id)
        return {
            "phc_id": phc_id,
            "phc_name": phc.get("name", phc_id),
            "district": phc.get("district", ""),
            "state": phc.get("state", phc.get("state_region", "")),
            "inventory": inventory
        }
