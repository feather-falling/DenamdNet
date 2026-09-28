"""
Core Redistribution Engine Orchestrator.
Coordinates target identification, candidate discovery, transfer calculation,
in-memory state management, and output file generation.
"""

import os
import json
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional

from ..models.state import (
    TargetRequirement,
    TransferRecord,
    UnresolvedRequirement,
    RedistributionResult
)
from ..utils.loaders import (
    normalize_country_name,
    load_json_file,
    load_static_network_data,
    resolve_redistribution_input_files
)
from .inventory_state import GlobalInventoryState
from .distance_calculator import DistanceCalculator
from .target_identifier import TargetIdentifier
from .candidate_discovery import CandidateDiscovery
from .transfer_calculator import TransferCalculator


class RedistributionEngine:
    """Deterministic Redistribution Engine for Primary Health Centre Supply Chains."""

    def __init__(
        self,
        base_dir: str = "data",
        output_dir: str = "output/redistribution",
        max_search_depth: int = 6,
        max_candidates_inspected: int = 100
    ):
        self.base_dir = base_dir
        self.output_dir = output_dir
        self.max_search_depth = max_search_depth
        self.max_candidates_inspected = max_candidates_inspected
        self.global_state = GlobalInventoryState()

    def run(
        self,
        country: Optional[str] = None,
        alerts_path: Optional[str] = None,
        predictions_path: Optional[str] = None,
        input_today_path: Optional[str] = None,
        save_outputs: bool = True
    ) -> RedistributionResult:
        """Executes the full redistribution workflow.
        
        1. Resolves and loads alerts.json, predictions.json, input_today.json.
        2. Detects country from input or predictions.
        3. Loads static master data (phcs, medicines, nearest neighbors).
        4. Initializes shared in-memory GlobalInventoryState.
        5. Identifies and quantifies targets (Alerts FIRST, then HIGH-risk, deduplicated).
        6. Discovers surplus sources (5 nearest neighbors first, then graph expansion).
        7. Executes transfers immediately on shared state.
        8. Truthfully recalculates post-redistribution operational state for all facilities.
        9. Generates output JSON files.
        """
        # 1. Resolve authoritative input files
        res_alerts_path, res_preds_path, res_inp_path = resolve_redistribution_input_files(
            alerts_path, predictions_path, input_today_path
        )

        alerts = load_json_file(res_alerts_path)
        predictions = load_json_file(res_preds_path)
        input_today = load_json_file(res_inp_path)

        # 2. Determine country
        detected_country = country
        if not detected_country:
            if isinstance(input_today, dict) and "country" in input_today:
                detected_country = input_today["country"]
            elif predictions and len(predictions) > 0:
                detected_country = predictions[0].get("country_code", "india")
            elif alerts and len(alerts) > 0:
                detected_country = alerts[0].get("country_code", "india")
            else:
                detected_country = "india"

        country_norm = normalize_country_name(detected_country)

        # Multi-country network redistribution
        if country_norm == "all":
            all_transfers: List[TransferRecord] = []
            all_unresolved: List[UnresolvedRequirement] = []
            all_next_day_state: List[Dict[str, Any]] = []
            total_targets = 0
            alert_priority_count = 0

            for c in ["india", "brazil", "south_africa", "china", "russia"]:
                c_engine = RedistributionEngine(
                    base_dir=self.base_dir,
                    output_dir=self.output_dir,
                    max_search_depth=self.max_search_depth,
                    max_candidates_inspected=self.max_candidates_inspected
                )
                c_result = c_engine.run(
                    country=c,
                    alerts_path=res_alerts_path,
                    predictions_path=res_preds_path,
                    input_today_path=res_inp_path,
                    save_outputs=False
                )
                all_transfers.extend(c_result.transfers_executed)
                all_unresolved.extend(c_result.unresolved_requirements)
                all_next_day_state.extend(c_result.next_day_state)
                total_targets += c_result.total_targets_evaluated
                alert_priority_count += c_result.alert_priority_targets

            total_vol = sum(t.transferred_units for t in all_transfers)
            fully_resolved = total_targets - len(all_unresolved)
            partially_resolved = sum(1 for u in all_unresolved if u.status == "PARTIALLY_RESOLVED")
            strictly_unresolved = sum(1 for u in all_unresolved if u.status == "UNRESOLVED")

            result = RedistributionResult(
                country="all",
                execution_timestamp=datetime.now(timezone.utc).isoformat(),
                total_targets_evaluated=total_targets,
                alert_priority_targets=alert_priority_count,
                transfers_executed=all_transfers,
                unresolved_requirements=all_unresolved,
                next_day_state=all_next_day_state,
                total_volume_transferred=total_vol,
                fully_resolved_count=fully_resolved,
                partially_resolved_count=partially_resolved,
                unresolved_count=strictly_unresolved
            )

            if save_outputs:
                self._save_results(result)

            return result

        # 3. Load static country network metadata
        network_data = load_static_network_data(self.base_dir, country_norm)
        phcs_meta = network_data["phcs"]
        meds_meta = network_data["medicines"]
        neighbors_map = network_data["nearest_neighbors"]

        # 4. Initialize shared in-memory inventory state
        input_records = input_today.get("records", []) if isinstance(input_today, dict) else []
        self.global_state.initialize(
            phcs=phcs_meta,
            medicines=meds_meta,
            input_records=input_records,
            predictions=predictions
        )

        # 5. Initialize distance calculator and candidate discovery
        distance_calc = DistanceCalculator(phcs_meta)
        discovery = CandidateDiscovery(
            neighbors_map=neighbors_map,
            phcs_meta=phcs_meta,
            distance_calc=distance_calc,
            max_search_depth=self.max_search_depth,
            max_candidates_inspected=self.max_candidates_inspected
        )

        # 6. Target Identification (Priority Alerts first, then HIGH-risk, deduplicated)
        targets = TargetIdentifier.identify_targets(
            alerts=alerts,
            predictions=predictions,
            global_state=self.global_state
        )

        # 7. Execute Transfers across targets using single shared state
        transfers_executed: List[TransferRecord] = []
        unresolved_list: List[UnresolvedRequirement] = []
        alert_priority_count = 0

        for target in targets:
            if target.is_alert_priority:
                alert_priority_count += 1

            initial_req = target.target_required_units

            # Discover eligible donor candidates
            candidate_sources = discovery.discover_eligible_sources(
                target_phc_id=target.phc_id,
                medicine_id=target.medicine_id,
                global_state=self.global_state
            )

            # Attempt transfer from candidates in order
            for src_id, _, dist_km in candidate_sources:
                if target.remaining_requirement <= 1e-4:
                    break

                t_record = TransferCalculator.execute_transfer(
                    target=target,
                    source_phc_id=src_id,
                    distance_km=dist_km,
                    global_state=self.global_state
                )
                if t_record:
                    transfers_executed.append(t_record)

            # Check final target resolution status
            if target.remaining_requirement > 1e-4:
                status = "PARTIALLY_RESOLVED" if target.remaining_requirement < initial_req else "UNRESOLVED"
                unresolved_list.append(UnresolvedRequirement(
                    target_phc_id=target.phc_id,
                    medicine_id=target.medicine_id,
                    medicine_name=target.medicine_name,
                    initial_stock=target.initial_stock,
                    required_units=initial_req,
                    transferred_units=initial_req - target.remaining_requirement,
                    remaining_requirement=target.remaining_requirement,
                    status=status
                ))

        # 8. Export post-redistribution operational state for ALL facilities
        next_day_state = self.global_state.export_all_states()

        # Compile metrics
        total_vol = sum(t.transferred_units for t in transfers_executed)
        fully_resolved = len(targets) - len(unresolved_list)
        partially_resolved = sum(1 for u in unresolved_list if u.status == "PARTIALLY_RESOLVED")
        strictly_unresolved = sum(1 for u in unresolved_list if u.status == "UNRESOLVED")

        timestamp_str = datetime.now(timezone.utc).isoformat()
        result = RedistributionResult(
            country=country_norm,
            execution_timestamp=timestamp_str,
            total_targets_evaluated=len(targets),
            alert_priority_targets=alert_priority_count,
            transfers_executed=transfers_executed,
            unresolved_requirements=unresolved_list,
            next_day_state=next_day_state,
            total_volume_transferred=total_vol,
            fully_resolved_count=fully_resolved,
            partially_resolved_count=partially_resolved,
            unresolved_count=strictly_unresolved
        )

        # 9. Save outputs
        if save_outputs:
            self._save_results(result)

        return result

    def _save_results(self, result: RedistributionResult) -> None:
        """Saves result files to output/redistribution/ and mirrors to outputs/redistribution/."""
        target_dirs = [
            self.output_dir,
            "outputs/redistribution"
        ]

        transfers_json = [t.to_dict() for t in result.transfers_executed]
        unresolved_json = [u.to_dict() for u in result.unresolved_requirements]
        results_payload = {
            "summary": result.summary_dict(),
            "transfers": transfers_json
        }

        for out_d in set(target_dirs):
            os.makedirs(out_d, exist_ok=True)

            # 1. next_day_phc_data.json
            with open(os.path.join(out_d, "next_day_phc_data.json"), "w", encoding="utf-8") as f:
                json.dump(result.next_day_state, f, indent=2)

            # 2. redistribution_results.json
            with open(os.path.join(out_d, "redistribution_results.json"), "w", encoding="utf-8") as f:
                json.dump(results_payload, f, indent=2)

            # 3. unresolved_requirements.json
            with open(os.path.join(out_d, "unresolved_requirements.json"), "w", encoding="utf-8") as f:
                json.dump(unresolved_json, f, indent=2)
