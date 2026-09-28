"""
Unit tests for Candidate Discovery, Neighbor Ordering, Graph Expansion, Cycles, and Depth Limits.
"""

from redistribution.engine.candidate_discovery import CandidateDiscovery
from redistribution.engine.distance_calculator import DistanceCalculator
from redistribution.engine.inventory_state import GlobalInventoryState


def test_first_neighbor_checked_first():
    """Verify 5 nearest neighbors are inspected in exact proximity order."""
    neighbors_map = {
        "TGT": [
            {"phc_id": "N1", "distance_km": 5.0},
            {"phc_id": "N2", "distance_km": 10.0},
            {"phc_id": "N3", "distance_km": 15.0},
            {"phc_id": "N4", "distance_km": 20.0},
            {"phc_id": "N5", "distance_km": 25.0}
        ]
    }
    phcs_meta = [
        {"phc_id": "TGT", "geography": {"latitude": 10.0, "longitude": 77.0}},
        {"phc_id": "N1", "geography": {"latitude": 10.05, "longitude": 77.0}},
        {"phc_id": "N2", "geography": {"latitude": 10.10, "longitude": 77.0}},
        {"phc_id": "N3", "geography": {"latitude": 10.15, "longitude": 77.0}},
        {"phc_id": "N4", "geography": {"latitude": 10.20, "longitude": 77.0}},
        {"phc_id": "N5", "geography": {"latitude": 10.25, "longitude": 77.0}},
    ]

    state = GlobalInventoryState()
    # Give all 5 positive surplus
    for nid in ["N1", "N2", "N3", "N4", "N5"]:
        state.get_or_create(nid, "MED-1", default_stock=2000.0, daily_req=10.0, safety=10.0)

    dist_calc = DistanceCalculator(phcs_meta)
    discovery = CandidateDiscovery(neighbors_map, phcs_meta, dist_calc)

    candidates = discovery.discover_eligible_sources("TGT", "MED-1", state)
    cand_ids = [c[0] for c in candidates[:5]]

    assert cand_ids == ["N1", "N2", "N3", "N4", "N5"]


def test_graph_expansion_and_cycle_prevention():
    """Verify graph expansion discovers neighbors of neighbors without infinite loops on cyclic graph."""
    # Graph with cycle: TGT -> A -> B -> C -> A
    neighbors_map = {
        "TGT": [{"phc_id": "A", "distance_km": 5.0}],
        "A": [{"phc_id": "TGT", "distance_km": 5.0}, {"phc_id": "B", "distance_km": 6.0}],
        "B": [{"phc_id": "A", "distance_km": 6.0}, {"phc_id": "C", "distance_km": 7.0}],
        "C": [{"phc_id": "A", "distance_km": 8.0}]  # Cycle back to A
    }
    phcs_meta = [
        {"phc_id": "TGT", "geography": {"latitude": 10.0, "longitude": 77.0}},
        {"phc_id": "A", "geography": {"latitude": 10.05, "longitude": 77.0}},
        {"phc_id": "B", "geography": {"latitude": 10.10, "longitude": 77.0}},
        {"phc_id": "C", "geography": {"latitude": 10.15, "longitude": 77.0}},
    ]

    state = GlobalInventoryState()
    # A has 0 surplus, B has 0 surplus, C has positive surplus!
    state.get_or_create("A", "MED-1", default_stock=10.0, daily_req=10.0, safety=10.0)  # protected=80, surplus=0
    state.get_or_create("B", "MED-1", default_stock=10.0, daily_req=10.0, safety=10.0)  # surplus=0
    state.get_or_create("C", "MED-1", default_stock=500.0, daily_req=10.0, safety=10.0) # surplus=420

    dist_calc = DistanceCalculator(phcs_meta)
    discovery = CandidateDiscovery(neighbors_map, phcs_meta, dist_calc, max_search_depth=4)

    candidates = discovery.discover_eligible_sources("TGT", "MED-1", state)
    cand_ids = [c[0] for c in candidates]

    # C must be discovered via A -> B -> C without crashing in infinite loop
    assert "C" in cand_ids
    assert cand_ids == ["C"]


def test_search_depth_limit_respected():
    """Verify search stops at max_search_depth."""
    # Chain: TGT -> A (depth 1) -> B (depth 2) -> C (depth 3)
    neighbors_map = {
        "TGT": [{"phc_id": "A"}],
        "A": [{"phc_id": "B"}],
        "B": [{"phc_id": "C"}],
        "C": []
    }
    phcs_meta = [
        {"phc_id": "TGT", "geography": {"latitude": 10.0, "longitude": 77.0}},
        {"phc_id": "A", "geography": {"latitude": 10.05, "longitude": 77.0}},
        {"phc_id": "B", "geography": {"latitude": 10.10, "longitude": 77.0}},
        {"phc_id": "C", "geography": {"latitude": 10.15, "longitude": 77.0}},
    ]
    state = GlobalInventoryState()
    state.get_or_create("C", "MED-1", default_stock=500.0, daily_req=10.0, safety=10.0)

    dist_calc = DistanceCalculator(phcs_meta)
    # Set max_search_depth = 2 (so B is queued at depth 2, its neighbors C would be depth 3 and excluded)
    discovery = CandidateDiscovery(neighbors_map, phcs_meta, dist_calc, max_search_depth=2)

    candidates = discovery.discover_eligible_sources("TGT", "MED-1", state)
    cand_ids = [c[0] for c in candidates]

    # C should NOT be discovered because depth limit = 2
    assert "C" not in cand_ids
