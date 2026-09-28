import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, Any, Tuple

class StockoutPredictor:
    """Calculates exact stock depletion days, stockout timestamp, and stockout probability."""

    def __init__(self, planning_horizon_days: int = 7):
        self.planning_horizon_days = planning_horizon_days

    def calculate_depletion(self, current_stock: float, forecast_quantiles: np.ndarray, as_of_time: datetime) -> Dict[str, Any]:
        """forecast_quantiles: array of shape (7, 3) containing P10, P50, P90 for 7 days ahead.
        Returns estimated_days, estimated_date, and stockout_prob.
        """
        p50_daily = forecast_quantiles[:, 1] # P50 daily demand over horizon
        total_p50_demand = float(np.sum(p50_daily))
        avg_daily_demand = float(np.mean(p50_daily))

        if current_stock <= 0:
            estimated_days = 0.0
            estimated_date = as_of_time.isoformat() + "Z"
            stockout_prob = 1.0
        elif avg_daily_demand <= 0:
            estimated_days = 999.0
            estimated_date = (as_of_time + timedelta(days=999)).isoformat() + "Z"
            stockout_prob = 0.0
        else:
            # Accumulate daily demand until stock runs out
            acc_demand = 0.0
            depletion_day = float(self.planning_horizon_days)
            for d, d_demand in enumerate(p50_daily):
                if acc_demand + d_demand >= current_stock:
                    rem_stock = current_stock - acc_demand
                    frac = rem_stock / (d_demand + 1e-5)
                    depletion_day = float(d) + float(frac)
                    break
                acc_demand += d_demand

            if acc_demand < current_stock:
                # Stock lasts longer than horizon
                extra_days = (current_stock - acc_demand) / (avg_daily_demand + 1e-5)
                depletion_day = float(self.planning_horizon_days) + float(extra_days)

            estimated_days = round(depletion_day, 2)
            depletion_seconds = int(estimated_days * 86400)
            estimated_date = (as_of_time + timedelta(seconds=depletion_seconds)).strftime("%Y-%m-%dT%H:%M:%SZ")

            # Stockout probability: based on P10/P90 variance
            p10_total = float(np.sum(forecast_quantiles[:, 0]))
            p90_total = float(np.sum(forecast_quantiles[:, 2]))
            if current_stock <= p10_total:
                stockout_prob = 0.95
            elif current_stock >= p90_total:
                stockout_prob = 0.05
            else:
                stockout_prob = float(np.clip(1.0 - (current_stock - p10_total) / (p90_total - p10_total + 1e-5), 0.05, 0.95))

        return {
            "estimated_days": estimated_days,
            "estimated_date": estimated_date,
            "stockout_probability": round(stockout_prob, 2),
            "daily_p50": round(avg_daily_demand, 2),
            "horizon_total_p50": round(total_p50_demand, 2)
        }
