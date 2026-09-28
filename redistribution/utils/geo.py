"""
Geographic distance calculations using the Haversine formula.
"""

import math
from typing import Dict, Any, Optional, Tuple


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculates great-circle distance between two points in kilometers.
    
    Uses standard WGS-84 Earth radius of 6371.0 km.
    """
    # Convert decimal degrees to radians
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(delta_phi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0) ** 2
    )
    # Clamp for numerical stability
    c = 2.0 * math.atan2(math.sqrt(min(1.0, max(0.0, a))), math.sqrt(max(0.0, 1.0 - a)))
    return 6371.0 * c


def extract_coordinates(phc_data: Dict[str, Any]) -> Optional[Tuple[float, float]]:
    """Safely extracts (latitude, longitude) from a PHC record."""
    if not isinstance(phc_data, dict):
        return None
        
    geo = phc_data.get("geography") or phc_data.get("coordinates") or phc_data
    if isinstance(geo, dict):
        lat = geo.get("latitude") or geo.get("lat")
        lon = geo.get("longitude") or geo.get("lon") or geo.get("lng")
        if lat is not None and lon is not None:
            try:
                return float(lat), float(lon)
            except (ValueError, TypeError):
                return None
    return None
