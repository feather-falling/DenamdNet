"""
Target identification and requirement quantification module.
Identifies priority alert facilities first, then ordinary HIGH-risk prediction targets,
filtering out non-shortages and deduplicating by (country_code, phc_id, medicine_id).
"""

from typing import Dict, Any, List, Set, Tuple, Optional
from ..models.state import TargetRequirement
from .inventory_state import GlobalInventoryState


class TargetIdentifier:
    """Identifies and prioritizes facilities and resources requiring redistribution."""

    @staticmethod
    def identify_targets(
        alerts: List[Dict[str, Any]],
        predictions: List[Dict[str, Any]],
        global_state: GlobalInventoryState,
        default_planning_horizon: int = 7
    ) -> List[TargetRequirement]:
        """Collects, validates, quantifies, and deduplicates all redistribution targets.
        
        Order of precedence:
        1. Alert-driven targets (processed FIRST).
        2. Ordinary prediction HIGH-risk targets.
        """
        targets: List[TargetRequirement] = []
        # Deduplication tracker: (country_code, phc_id, medicine_id) -> TargetRequirement
        seen_targets: Dict[Tuple[str, str, str], TargetRequirement] = {}

        # Build prediction index: (phc_id, medicine_id) -> pred_record
        pred_by_phc_med: Dict[Tuple[str, str], Dict[str, Any]] = {}
        # Also build index by (phc_id, medicine_name.lower()) for correlated_resources matching
        pred_by_phc_medname: Dict[Tuple[str, str], Dict[str, Any]] = {}

        for p in predictions:
            phc_id = p.get("phc_id", "")
            med_id = p.get("medicine_id", "")
            med_name = p.get("medicine_name", "").strip().lower()
            pred_by_phc_med[(phc_id, med_id)] = p
            if med_name:
                pred_by_phc_medname[(phc_id, med_name)] = p

        # -------------------------------------------------------------
        # STEP 1: Process Alert PHCs (PRIORITY TARGETS)
        # -------------------------------------------------------------
        for alert in alerts:
            phc_id = alert.get("phc_id")
            country_code = alert.get("country_code", "IN")
            alert_id = alert.get("alert_id")
            correlated_resources = alert.get("correlated_resources", [])
            primary_driver = alert.get("primary_driver")

            if not phc_id:
                continue

            # Resources to evaluate: primary driver + correlated resources
            candidate_res_names = list(correlated_resources)
            if primary_driver and primary_driver not in candidate_res_names:
                candidate_res_names.insert(0, primary_driver)

            for res_name in candidate_res_names:
                clean_name = str(res_name).strip().lower()
                
                # Match to prediction record by name or by ID
                pred_rec = pred_by_phc_medname.get((phc_id, clean_name))
                if not pred_rec:
                    # Try matching as medicine_id
                    pred_rec = pred_by_phc_med.get((phc_id, res_name))

                if not pred_rec:
                    # Prediction record not found for this correlated resource at this PHC, skip
                    continue

                med_id = pred_rec["medicine_id"]
                med_name = pred_rec.get("medicine_name", med_id)
                key = (country_code, phc_id, med_id)

                if key in seen_targets:
                    # Already captured; ensure marked as alert priority
                    seen_targets[key].is_alert_priority = True
                    if not seen_targets[key].alert_id:
                        seen_targets[key].alert_id = alert_id
                    continue

                # Query current in-memory inventory state
                item_state = global_state.get(phc_id, med_id)
                if item_state is not None:
                    current_stock = item_state.current_stock
                    daily_forecast = item_state.daily_requirement
                    safety_stock = item_state.safety_stock
                    horizon = item_state.planning_horizon_days
                    district = item_state.district
                    state_region = item_state.state_region
                else:
                    current_stock = float(pred_rec.get("current_stock", 0.0))
                    daily_forecast = float(pred_rec.get("forecast_demand", {}).get("daily", 10.0))
                    safety_stock = float(pred_rec.get("inventory_protection", {}).get("safety_stock", 10.0))
                    horizon = int(pred_rec.get("forecast_demand", {}).get("planning_horizon_days", default_planning_horizon))
                    district = pred_rec.get("district", "")
                    state_region = pred_rec.get("state_region", "")

                planning_req = daily_forecast * horizon
                protected_target_stock = planning_req + safety_stock
                required_units = max(0.0, protected_target_stock - current_stock)

                risk_level = pred_rec.get("risk", {}).get("level", "LOW")

                # RULE 12: Ignore correlated resources that have NO quantitative shortage requirement.
                # Prefer resources that are actually HIGH risk or demonstrably below protected inventory.
                if required_units > 0 and (risk_level == "HIGH" or current_stock < protected_target_stock):
                    target_obj = TargetRequirement(
                        country_code=country_code,
                        phc_id=phc_id,
                        medicine_id=med_id,
                        medicine_name=med_name,
                        district=district,
                        state_region=state_region,
                        initial_stock=current_stock,
                        daily_forecast=daily_forecast,
                        safety_stock=safety_stock,
                        planning_horizon_days=horizon,
                        target_required_units=required_units,
                        remaining_requirement=required_units,
                        is_alert_priority=True,
                        alert_id=alert_id,
                        risk_level=risk_level
                    )
                    seen_targets[key] = target_obj
                    targets.append(target_obj)

        # -------------------------------------------------------------
        # STEP 2: Process Ordinary Prediction Targets (risk.level == HIGH)
        # -------------------------------------------------------------
        for pred in predictions:
            risk = pred.get("risk", {})
            risk_level = risk.get("level", "LOW")
            if risk_level != "HIGH":
                continue

            phc_id = pred.get("phc_id")
            med_id = pred.get("medicine_id")
            country_code = pred.get("country_code", "IN")
            if not phc_id or not med_id:
                continue

            key = (country_code, phc_id, med_id)
            if key in seen_targets:
                # Already captured (e.g. under alert), avoid duplicate requirement
                continue

            item_state = global_state.get(phc_id, med_id)
            if item_state is not None:
                current_stock = item_state.current_stock
                daily_forecast = item_state.daily_requirement
                safety_stock = item_state.safety_stock
                horizon = item_state.planning_horizon_days
                district = item_state.district
                state_region = item_state.state_region
            else:
                current_stock = float(pred.get("current_stock", 0.0))
                daily_forecast = float(pred.get("forecast_demand", {}).get("daily", 10.0))
                safety_stock = float(pred.get("inventory_protection", {}).get("safety_stock", 10.0))
                horizon = int(pred.get("forecast_demand", {}).get("planning_horizon_days", default_planning_horizon))
                district = pred.get("district", "")
                state_region = pred.get("state_region", "")

            planning_req = daily_forecast * horizon
            protected_target_stock = planning_req + safety_stock
            required_units = max(0.0, protected_target_stock - current_stock)

            if required_units > 0:
                target_obj = TargetRequirement(
                    country_code=country_code,
                    phc_id=phc_id,
                    medicine_id=med_id,
                    medicine_name=pred.get("medicine_name", med_id),
                    district=district,
                    state_region=state_region,
                    initial_stock=current_stock,
                    daily_forecast=daily_forecast,
                    safety_stock=safety_stock,
                    planning_horizon_days=horizon,
                    target_required_units=required_units,
                    remaining_requirement=required_units,
                    is_alert_priority=False,
                    alert_id=None,
                    risk_level=risk_level
                )
                seen_targets[key] = target_obj
                targets.append(target_obj)

        # Sort so that alert priority targets come FIRST
        targets.sort(key=lambda t: (not t.is_alert_priority, -t.target_required_units))
        return targets
