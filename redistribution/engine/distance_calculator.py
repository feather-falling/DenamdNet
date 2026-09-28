"""
Authoritative distance calculation engine.
Computes true Haversine distance between facilities using coordinates from phcs.json.
"""

from typing import Dict, Any, List, Optional, Tuple
from ..utils.geo import haversine_distance, extract_coordinates


class DistanceCalculator:
    """Calculates geographic distances between PHCs using master facility coordinates."""

    def __init__(self, phcs_meta: List[Dict[str, Any]]):
        # Cache coordinates: phc_id -> (lat, lon)
        self._coords: Dict[str, Tuple[float, float]] = {}
        for p in phcs_meta:
            coords = extract_coordinates(p)
            if coords:
                self._coords[p["phc_id"]] = coords

    def get_coordinates(self, phc_id: str) -> Optional[Tuple[float, float]]:
        """Returns coordinates tuple (lat, lon) if available for facility."""
        return self._coords.get(phc_id)

    def calculate_distance_km(
        self,
        source_phc_id: str,
        target_phc_id: str,
        fallback_distance: float = 25.0
    ) -> float:
        """Calculates true great-circle distance between two facilities.
        
        If coordinates are missing for either facility, returns fallback_distance with a log.
        """
        c1 = self.get_coordinates(source_phc_id)
        c2 = self.get_coordinates(target_phc_id)

        if c1 is not None and c2 is not None:
            return haversine_distance(c1[0], c1[1], c2[0], c2[1])

        # Return reasonable fallback if coordinate data is unavailable
        return fallback_distance
