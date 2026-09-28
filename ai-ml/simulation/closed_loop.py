import numpy as np
import pandas as pd
from typing import Dict, Any, List

try:
    from simulation.simulator import InventorySimulator
    from inference.prediction_service import PredictionService
    from models.baselines import MovingAverageBaseline
except ImportError:
    from .simulator import InventorySimulator
    from ..inference.prediction_service import PredictionService
    from ..models.baselines import MovingAverageBaseline

class ClosedLoopSimulation:
    """Executes closed-loop simulation across timesteps:
    ML predict -> Redistribution proposal -> Transfer applied to inventory -> Next state -> Repeat.
    """

    def __init__(self, initial_df: pd.DataFrame, med_catalog: List[Dict[str, Any]] = [], phc_catalog: List[Dict[str, Any]] = []):
        self.simulator = InventorySimulator(initial_df)
        self.service = PredictionService()
        self.med_catalog = med_catalog
        self.phc_catalog = phc_catalog
        self.baseline = MovingAverageBaseline()

    def run_simulation(self, steps: int = 7) -> Dict[str, Any]:
        history = []

        for step in range(steps):
            current_df = self.simulator.state_df.reset_index(drop=True)

            # 1. ML Forecast & Predictions
            q_preds = self.baseline.predict(current_df)
            anom_scores = np.random.uniform(0.1, 0.4, size=len(current_df))
            anom_detected = anom_scores > 0.35

            records = self.service.generate_sharma_records(
                current_df, q_preds, anom_scores, anom_detected, self.med_catalog, self.phc_catalog
            )

            # 2. Identify High Risk facilities requiring redistribution
            high_risk = [r for r in records if r["risk"]["level"] == "HIGH"]
            surplus = [r for r in records if r["risk"]["level"] == "LOW" and r["current_stock"] > r["inventory_protection"]["safety_stock"] * 2]

            transfers = []
            for hr in high_risk[:5]:
                for sur in surplus[:5]:
                    if sur["medicine_id"] == hr["medicine_id"] and sur["phc_id"] != hr["phc_id"]:
                        transfer_qty = min(300, sur["current_stock"] - sur["inventory_protection"]["safety_stock"])
                        if transfer_qty > 50:
                            transfers.append({
                                "source_phc": sur["phc_id"],
                                "dest_phc": hr["phc_id"],
                                "medicine_id": hr["medicine_id"],
                                "quantity": transfer_qty
                            })

            self.simulator.apply_transfers(transfers)

            history.append({
                "step": step,
                "high_risk_count": len(high_risk),
                "transfers_proposed": len(transfers),
                "total_transfer_volume": sum(t["quantity"] for t in transfers)
            })

            next_day_df = current_df.copy()
            next_day_df["date"] = pd.to_datetime(next_day_df["date"]) + pd.Timedelta(days=1)
            self.simulator.step_next_day(next_day_df)

        return {
            "steps_completed": steps,
            "simulation_history": history
        }
