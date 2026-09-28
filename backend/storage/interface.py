"""
Abstract Storage Interface for BRICS operational backend.
Enables pluggable backend storage: JSON file-based now, PostgreSQL later.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class StorageInterface(ABC):
    """Storage contract separating operational business logic from persistence implementation."""

    @abstractmethod
    def get_phc(self, phc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves PHC master metadata by facility ID."""
        pass

    @abstractmethod
    def list_phcs(self, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists PHCs filtered optionally by country."""
        pass

    @abstractmethod
    def get_phc_inventory(self, phc_id: str) -> List[Dict[str, Any]]:
        """Retrieves current or post-redistribution inventory items for a specific PHC."""
        pass

    @abstractmethod
    def get_predictions(
        self,
        phc_id: Optional[str] = None,
        medicine_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries Sharma redistribution prediction records with optional filters."""
        pass

    @abstractmethod
    def get_alerts(
        self,
        phc_id: Optional[str] = None,
        district: Optional[str] = None,
        severity: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries disease outbreak alerts with optional filters."""
        pass

    @abstractmethod
    def get_redistribution_results(self) -> Optional[Dict[str, Any]]:
        """Retrieves the latest redistribution run results."""
        pass

    @abstractmethod
    def get_next_day_phc_data(self) -> List[Dict[str, Any]]:
        """Retrieves the latest complete post-redistribution operational state."""
        pass

    @abstractmethod
    def save_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves a new PHC operational resource request."""
        pass

    @abstractmethod
    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a resource request by unique request ID."""
        pass

    @abstractmethod
    def list_requests(
        self,
        phc_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists resource requests with optional filtering by PHC ID and status."""
        pass

    @abstractmethod
    def update_request(
        self,
        request_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Updates fields of an existing resource request."""
        pass
