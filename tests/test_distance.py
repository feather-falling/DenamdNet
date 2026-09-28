"""
Unit tests for Distance Calculation and Haversine formula.
"""

from redistribution.utils.geo import haversine_distance, extract_coordinates
from redistribution.engine.distance_calculator import DistanceCalculator


def test_haversine_formula_accuracy():
    """Verify haversine formula against known coordinates:
    Delhi (28.6139, 77.2090) to Agra (27.1767, 78.0081) is approximately 175-185 km.
    """
    delhi_lat, delhi_lon = 28.6139, 77.2090
    agra_lat, agra_lon = 27.1767, 78.0081

    dist = haversine_distance(delhi_lat, delhi_lon, agra_lat, agra_lon)
    assert 170.0 < dist < 190.0


def test_extract_coordinates_formats():
    """Verify coordinate extraction from various schema shapes."""
    phc_standard = {"geography": {"latitude": 28.6, "longitude": 77.2}}
    assert extract_coordinates(phc_standard) == (28.6, 77.2)

    phc_flat = {"lat": 12.34, "lon": 56.78}
    assert extract_coordinates(phc_flat) == (12.34, 56.78)

    phc_missing = {"geography": {}}
    assert extract_coordinates(phc_missing) is None


def test_missing_coordinates_fallback():
    """Verify distance calculator gracefully uses fallback when coordinates are missing."""
    phcs_meta = [
        {"phc_id": "P1", "geography": {"latitude": 28.6, "longitude": 77.2}},
        {"phc_id": "P2", "geography": {}} # missing coords
    ]
    calc = DistanceCalculator(phcs_meta)
    dist = calc.calculate_distance_km("P1", "P2", fallback_distance=35.0)
    assert dist == 35.0
