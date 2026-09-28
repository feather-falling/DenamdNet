"""
Redistribution service coordinating the redistribution engine and results querying.
"""

from typing import Dict, Any, List, Optional
from ..storage.interface import StorageInterface
from redistribution.engine.redistribution_engine import RedistributionEngine
from redistribution.models.state import RedistributionResult


class RedistributionService:
    def __init__(self, storage: StorageInterface):
        self.storage = storage
        self._last_result: Optional[RedistributionResult] = None

    def run_redistribution(
        self,
        country: Optional[str] = "india",
        max_search_depth: int = 4,
        max_candidates_inspected: int = 50
    ) -> Dict[str, Any]:
        """Runs the redistribution engine and returns summary."""
        engine = RedistributionEngine(
            max_search_depth=max_search_depth,
            max_candidates_inspected=max_candidates_inspected
        )
        result = engine.run(country=country, save_outputs=True)
        self._last_result = result
        return {
            "status": "COMPLETED",
            "summary": result.summary_dict(),
            "transfers_count": len(result.transfers_executed)
        }

    def get_status(self) -> Dict[str, Any]:
        """Retrieves status of redistribution engine."""
        if self._last_result:
            return {
                "status": "COMPLETED",
                "last_run_timestamp": self._last_result.execution_timestamp,
                "summary": self._last_result.summary_dict()
            }
        
        # Check if saved results exist
        saved = self.storage.get_redistribution_results()
        if saved and "summary" in saved:
            return {
                "status": "COMPLETED",
                "last_run_timestamp": saved["summary"].get("execution_timestamp"),
                "summary": saved["summary"]
            }
        return {
            "status": "IDLE",
            "message": "No redistribution runs have been executed yet."
        }

    def get_results(self) -> Optional[Dict[str, Any]]:
        """Retrieves latest redistribution transfers and summary."""
        return self.storage.get_redistribution_results()

    def get_next_day_phc_data(self) -> List[Dict[str, Any]]:
        """Retrieves post-redistribution operational state."""
        return self.storage.get_next_day_phc_data()
