import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional

class MultiResourcePatternDetector:
    """Multi-resource disease/outbreak pattern detector analyzing correlated resource spikes over time."""

    def __init__(self, confidence_threshold: float = 0.50):
        self.confidence_threshold = confidence_threshold

    def _evaluate_pattern_match(self, resource_spikes: Dict[str, float], primary_keys: List[str], negative_keys: List[str] = []) -> float:
        """Calculates pattern match score based on presence and magnitude of correlated resource spikes."""
        matched_scores = []
        for key in primary_keys:
            # Check if any medicine in resource_spikes matches key (substring or ID match)
            matching_vals = [val for med_name, val in resource_spikes.items() if key.lower() in med_name.lower()]
            if matching_vals:
                matched_scores.append(max(matching_vals))

        if not matched_scores:
            return 0.0

        # Negative evidence penalty (e.g. Dengue diagnostic spikes during pure Malaria pattern)
        neg_penalty = 0.0
        for neg_key in negative_keys:
            matching_negs = [val for med_name, val in resource_spikes.items() if neg_key.lower() in med_name.lower()]
            if matching_negs and max(matching_negs) > 1.5:
                neg_penalty += 0.25

        base_score = np.mean(matched_scores) * (len(matched_scores) / len(primary_keys))
        return float(np.clip(base_score - neg_penalty, 0.0, 1.0))

    def detect_patterns(self, df: pd.DataFrame, anomaly_scores: np.ndarray, med_catalog: List[Dict[str, Any]] = []) -> List[Dict[str, Any]]:
        """Scans PHCs for multi-resource correlated spikes and detects disease/outbreak patterns.
        Does NOT use simulator event labels. Infer patterns purely from healthcare signals.
        """
        df = df.copy()
        df["anomaly_score"] = anomaly_scores
        demand_col = "demand_units" if "demand_units" in df.columns else "consumed_units"

        # Build medicine name mapping
        med_id_to_name = {m["medicine_id"]: m.get("name", m["medicine_id"]) for m in med_catalog}

        # Calculate demand velocity (ratio of current demand to 14-day rolling mean)
        grouped = df.groupby(["phc_id", "medicine_id"])
        roll_mean = grouped[demand_col].transform(lambda s: s.shift(1).rolling(14, min_periods=1).mean()).fillna(1.0)
        df["velocity"] = (df[demand_col] + 1.0) / (roll_mean + 1.0)

        alerts = []
        # Group by PHC and date
        for (phc_id, dt), group in df.groupby(["phc_id", "date"]):
            # Filter for items with elevated velocity or anomaly score
            spikes = {}
            for _, row in group.iterrows():
                m_name = med_id_to_name.get(row["medicine_id"], row["medicine_id"])
                if row["velocity"] > 1.2 or row["anomaly_score"] > 0.3:
                    spikes[m_name] = float(np.clip((row["velocity"] - 1.0) / 2.0, 0.0, 1.0))

            if not spikes:
                continue

            # Evaluate standard disease pattern signatures
            dengue_score = self._evaluate_pattern_match(spikes, ["Paracetamol", "ORS", "Diagnostic", "Saline", "Hematology"], negative_keys=[])
            malaria_score = self._evaluate_pattern_match(spikes, ["Malaria", "Artemether", "Paracetamol", "Saline"], negative_keys=["Dengue"])
            covid_score = self._evaluate_pattern_match(spikes, ["Respiratory", "Paracetamol", "Mask", "Oxygen", "PPE"], negative_keys=[])
            diarrhoeal_score = self._evaluate_pattern_match(spikes, ["ORS", "Zinc", "Stool", "Saline"], negative_keys=[])
            flu_score = self._evaluate_pattern_match(spikes, ["Respiratory", "Paracetamol", "Pediatric", "Mask"], negative_keys=["Oxygen"])

            scores = {
                "DENGUE_LIKE": dengue_score,
                "MALARIA_LIKE": malaria_score,
                "COVID_RESPIRATORY_LIKE": covid_score,
                "ACUTE_DIARRHOEAL_LIKE": diarrhoeal_score,
                "INFLUENZA_RESPIRATORY_LIKE": flu_score
            }

            best_pattern, best_score = max(scores.items(), key=lambda x: x[1])

            if best_score >= self.confidence_threshold:
                district = group["district"].iloc[0] if "district" in group.columns else "DEFAULT"
                country = group["country_code"].iloc[0] if "country_code" in group.columns else phc_id.split("-")[0]

                severity = "EMERGENCY" if best_score >= 0.80 else ("WARNING" if best_score >= 0.60 else "WATCH")

                alert_record = {
                    "alert_id": f"ALT-{phc_id}-{pd.to_datetime(dt).strftime('%Y%m%d')}-{best_pattern[:3]}",
                    "timestamp": pd.to_datetime(dt).isoformat() + "Z",
                    "country_code": country,
                    "phc_id": phc_id,
                    "district": district,
                    "pattern_type": best_pattern,
                    "confidence_score": round(best_score, 2),
                    "severity": severity,
                    "correlated_resources": list(spikes.keys()),
                    "primary_driver": max(spikes.items(), key=lambda x: x[1])[0] if spikes else "Unknown",
                    "spatial_cluster_size": 1,
                    "recommended_actions": [
                        f"Pre-position stock of {best_pattern} essential items",
                        "Alert district health officer for epidemiological verification",
                        "Increase safety stock buffer at facility"
                    ]
                }
                alerts.append(alert_record)

        return alerts
