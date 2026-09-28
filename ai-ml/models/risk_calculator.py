import numpy as np
from typing import Dict, Any

class SafetyStockAndRiskCalculator:
    """Calculates safety stock levels and operational risk score according to blueprint formulas."""

    def __init__(self, lead_time_hours: float = 8.0, default_criticality: str = "ESSENTIAL"):
        self.lead_time_hours = lead_time_hours
        self.default_criticality = default_criticality
        self.kappa = {
            "CRITICAL": 1.15,
            "ESSENTIAL": 1.05,
            "STANDARD": 1.00
        }

    def calculate_safety_stock(self, daily_demand_std: float, criticality_class: str = "ESSENTIAL") -> int:
        """Safety stock = Z * sigma_L * sqrt(L_days) * kappa."""
        lead_time_days = self.lead_time_hours / 24.0
        z_score = 1.65 # 95% service level
        kappa = self.kappa.get(criticality_class.upper(), 1.05)

        sigma_L = max(daily_demand_std, 1.0)
        ss = z_score * sigma_L * np.sqrt(lead_time_days) * kappa
        return int(np.ceil(ss))

    def calculate_risk_score(
        self, 
        current_stock: float, 
        safety_stock: float, 
        estimated_days: float, 
        stockout_prob: float, 
        anomaly_score: float, 
        criticality_class: str = "ESSENTIAL"
    ) -> Dict[str, Any]:
        """Calculates composite operational risk score (0.0 to 1.0) and level (LOW, MEDIUM, HIGH)."""
        # 1. Stockout probability weight (45%)
        w_prob = stockout_prob

        # 2. Urgency weight (35%): higher if estimated_days is low (< 3 days)
        if estimated_days <= 1.0:
            w_urgency = 1.0
        elif estimated_days <= 3.0:
            w_urgency = 0.75
        elif estimated_days <= 7.0:
            w_urgency = 0.40
        else:
            w_urgency = 0.10

        # 3. Anomaly score weight (10%)
        w_anomaly = anomaly_score

        # 4. Cover gap weight (10%): ratio of safety stock deficit
        deficit = max(0.0, safety_stock - current_stock)
        w_gap = min(1.0, deficit / (safety_stock + 1e-5))

        kappa = self.kappa.get(criticality_class.upper(), 1.05)
        raw_score = (0.45 * w_prob + 0.35 * w_urgency + 0.10 * w_anomaly + 0.10 * w_gap) * kappa
        score = float(np.clip(raw_score, 0.0, 1.0))

        # Risk level cutoffs
        if score >= 0.60:
            level = "HIGH"
        elif score >= 0.30:
            level = "MEDIUM"
        else:
            level = "LOW"

        return {
            "score": round(score, 2),
            "level": level
        }
