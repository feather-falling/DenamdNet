import os
import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List

try:
    from models.stockout_predictor import StockoutPredictor
    from models.risk_calculator import SafetyStockAndRiskCalculator
    from models.anomaly_detector import LayeredAnomalyDetector
    from models.pattern_detector import MultiResourcePatternDetector
except ImportError:
    from ..models.stockout_predictor import StockoutPredictor
    from ..models.risk_calculator import SafetyStockAndRiskCalculator
    from ..models.anomaly_detector import LayeredAnomalyDetector
    from ..models.pattern_detector import MultiResourcePatternDetector

class PredictionService:
    """Prediction Service generating Sharma's exact redistribution JSON contract and separate disease alert JSONs."""

    def __init__(self, planning_horizon_days: int = 7):
        self.stockout_predictor = StockoutPredictor(planning_horizon_days=planning_horizon_days)
        self.risk_calculator = SafetyStockAndRiskCalculator()
        self.anomaly_detector = LayeredAnomalyDetector()
        self.pattern_detector = MultiResourcePatternDetector()

    def generate_sharma_records(
        self, 
        df: pd.DataFrame, 
        forecast_quantiles: np.ndarray, 
        anomaly_scores: np.ndarray, 
        anomaly_detected: np.ndarray, 
        med_catalog: List[Dict[str, Any]], 
        phc_catalog: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        med_map = {m["medicine_id"]: m for m in med_catalog}
        phc_map = {p["phc_id"]: p for p in phc_catalog}

        records = []

        for i, row in df.iterrows():
            m_id = row["medicine_id"]
            p_id = row["phc_id"]

            m_info = med_map.get(m_id, {"name": m_id, "unit": "tablet", "category": "ESSENTIAL"})
            p_info = phc_map.get(p_id, {"country": "IN", "state": "Uttar Pradesh", "district": "Meerut"})

            as_of_dt = pd.to_datetime(row["date"])
            cur_stock = float(row["closing_stock"]) if "closing_stock" in row else float(row.get("opening_stock", 0))

            q_preds = forecast_quantiles[i] # (7, 3)
            p50_daily = float(np.mean(q_preds[:, 1]))
            total_p50 = float(np.sum(q_preds[:, 1]))

            # Stockout calculation
            so_info = self.stockout_predictor.calculate_depletion(cur_stock, q_preds, as_of_dt)

            # Safety stock & risk calculation
            std_demand = float(np.std(q_preds[:, 1])) if np.std(q_preds[:, 1]) > 0 else 5.0
            crit_class = m_info.get("category", "ESSENTIAL")
            ss = self.risk_calculator.calculate_safety_stock(std_demand, crit_class)

            risk_info = self.risk_calculator.calculate_risk_score(
                current_stock=cur_stock,
                safety_stock=ss,
                estimated_days=so_info["estimated_days"],
                stockout_prob=so_info["stockout_probability"],
                anomaly_score=float(anomaly_scores[i]),
                criticality_class=crit_class
            )

            country = p_info.get("country", "India")
            if "country_code" in p_info and p_info["country_code"]:
                ccode = p_info["country_code"].upper()
            elif country.lower() in ["india", "in"]:
                ccode = "IN"
            elif country.lower() in ["brazil", "br", "brasil"]:
                ccode = "BR"
            elif country.lower() in ["south africa", "south_africa", "za"]:
                ccode = "ZA"
            elif country.lower() in ["china", "cn"]:
                ccode = "CN"
            elif country.lower() in ["russia", "ru", "russian_federation"]:
                ccode = "RU"
            elif p_id.startswith("CN-"):
                ccode = "CN"
            elif p_id.startswith("RU-"):
                ccode = "RU"
            elif p_id.startswith("BR-"):
                ccode = "BR"
            elif p_id.startswith("ZA-"):
                ccode = "ZA"
            else:
                ccode = "IN"

            rec = {
                "timestamp": as_of_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "phc_id": p_id,
                "country_code": ccode,
                "state_region": p_info.get("state", "State"),
                "district": p_info.get("district", "District"),
                "medicine_id": m_id,
                "medicine_name": m_info.get("name", m_id),
                "unit": m_info.get("unit", "tablet"),
                "current_stock": int(round(cur_stock)),
                "forecast_demand": {
                    "daily": int(round(p50_daily)),
                    "planning_horizon_days": 7,
                    "total": int(round(total_p50))
                },
                "stockout": {
                    "estimated_days": round(so_info["estimated_days"], 2),
                    "estimated_date": so_info["estimated_date"]
                },
                "risk": {
                    "score": round(risk_info["score"], 2),
                    "level": risk_info["level"]
                },
                "anomaly": {
                    "score": round(float(anomaly_scores[i]), 2),
                    "detected": bool(anomaly_detected[i])
                },
                "inventory_protection": {
                    "safety_stock": int(ss),
                    "lead_time_hours": 8
                }
            }
            records.append(rec)

        return records

    def generate_disease_alerts(
        self, 
        df: pd.DataFrame, 
        anomaly_scores: np.ndarray, 
        med_catalog: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        return self.pattern_detector.detect_patterns(df, anomaly_scores, med_catalog)
