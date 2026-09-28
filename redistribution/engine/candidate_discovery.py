"""
Candidate source discovery engine.
Performs two-phase discovery:
Phase 1: 5 nearest neighbors in increasing proximity order from nearest_neighbors.json.
Phase 2: Graph expansion with visited tracking, cycle prevention, and distance sorting relative to original target.
"""

from typing import Dict, Any, List, Set, Tuple, Optional
from collections import deque
from .inventory_state import GlobalInventoryState
from .distance_calculator import DistanceCalculator


class CandidateDiscovery:
    """Discovers eligible donor facilities with transferable surplus."""

    def __init__(
        self,
        neighbors_map: Dict[str, List[Dict[str, Any]]],
        phcs_meta: List[Dict[str, Any]],
        distance_calc: DistanceCalculator,
        max_search_depth: int = 6,
        max_candidates_inspected: int = 100
    ):
        self.neighbors_map = neighbors_map
        self.phcs_meta = {p["phc_id"]: p for p in phcs_meta}
        self.distance_calc = distance_calc
        self.max_search_depth = max_search_depth
        self.max_candidates_inspected = max_candidates_inspected

    def _get_neighbor_ids(self, phc_id: str) -> List[str]:
        """Extracts ordered neighbor PHC IDs from neighbors map."""
        raw_list = self.neighbors_map.get(phc_id, [])
        neighbor_ids = []
        for item in raw_list:
            if isinstance(item, dict) and "phc_id" in item:
                neighbor_ids.append(item["phc_id"])
            elif isinstance(item, str):
                neighbor_ids.append(item)
        return neighbor_ids

    def discover_eligible_sources(
        self,
        target_phc_id: str,
        medicine_id: str,
        global_state: GlobalInventoryState
    ) -> List[Tuple[str, float, float]]:
        """Finds eligible donor facilities for a target and medicine.
        
        Returns a list of tuples: (source_phc_id, transferable_surplus, distance_from_target_km)
        in the strict precedence order:
        1. Direct 5 nearest neighbors (in proximity order).
        2. Graph-expanded candidates sorted by actual distance from the ORIGINAL target.
        """
        results: List[Tuple[str, float, float]] = []
        visited_phcs: Set[str] = {target_phc_id}

        # ---------------------------------------------------------------------
        # PHASE 1: Direct 5 Nearest Neighbors
        # ---------------------------------------------------------------------
        direct_5 = self._get_neighbor_ids(target_phc_id)[:5]

        for cand_id in direct_5:
            visited_phcs.add(cand_id)
            if cand_id not in self.phcs_meta:
                continue

            cand_state = global_state.get(cand_id, medicine_id)
            if cand_state is None:
                continue

            surplus = cand_state.transferable_surplus
            if surplus > 0:
                dist = self.distance_calc.calculate_distance_km(target_phc_id, cand_id)
                results.append((cand_id, surplus, dist))

        # ---------------------------------------------------------------------
        # PHASE 2: Graph Expansion (if 5 nearest neighbors don't suffice or for full candidate set)
        # ---------------------------------------------------------------------
        # BFS Queue holds: (phc_id, current_depth)
        queue: deque = deque()
        for cand_id in direct_5:
            queue.append((cand_id, 1))

        expanded_candidates: List[Tuple[str, float, float]] = []
        inspected_count = 0

        while queue and inspected_count < self.max_candidates_inspected:
            current_phc, depth = queue.popleft()
            if depth >= self.max_search_depth:
                continue

            current_neighbors = self._get_neighbor_ids(current_phc)
            for nbr_id in current_neighbors:
                if nbr_id in visited_phcs:
                    continue

                visited_phcs.add(nbr_id)
                inspected_count += 1
                queue.append((nbr_id, depth + 1))

                if nbr_id not in self.phcs_meta:
                    continue

                nbr_state = global_state.get(nbr_id, medicine_id)
                if nbr_state is None:
                    continue

                surplus = nbr_state.transferable_surplus
                if surplus > 0:
                    # RULE 22: Calculate actual distance from the ORIGINAL target!
                    dist_from_orig_target = self.distance_calc.calculate_distance_km(target_phc_id, nbr_id)
                    expanded_candidates.append((nbr_id, surplus, dist_from_orig_target))

                if inspected_count >= self.max_candidates_inspected:
                    break

        # Sort expanded candidates by geographic distance from ORIGINAL target
        expanded_candidates.sort(key=lambda x: x[2])

        # Combine Phase 1 (direct neighbors in proximity order) + Phase 2 (expanded sorted by distance)
        results.extend(expanded_candidates)
        return results
