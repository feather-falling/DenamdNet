import pandas as pd
import numpy as np

class StockReconciler:
    """Reconciles inventory movements and flags demand censoring."""

    def reconcile_and_flag_censoring(self, inv_df: pd.DataFrame, dem_df: pd.DataFrame) -> pd.DataFrame:
        """Merges inventory and demand, verifies conservation law, and flags demand censoring."""
        merged = pd.merge(
            inv_df, 
            dem_df[["date", "phc_id", "medicine_id", "demand_units", "patient_visits", "diagnostic_usage_units"]],
            on=["date", "phc_id", "medicine_id"],
            how="left"
        )

        # Inventory balance: opening + received + incoming - consumed - outgoing
        calculated_closing = (
            merged["opening_stock"] + 
            merged["received_units"] + 
            merged["incoming_transfer_units"] - 
            merged["consumed_units"] - 
            merged["outgoing_transfer_units"]
        )

        # Check reconciliation disparity
        recon_diff = (merged["closing_stock"] - calculated_closing).abs()
        merged["recon_error"] = recon_diff > 1.0  # Allow 1 unit float tolerance

        # Flag demand censoring: when stock drops to 0 or unmet demand occurs, observed consumed_units is censored
        merged["is_censored"] = (
            (merged["closing_stock"] <= 0) | 
            (merged["unmet_demand_units"] > 0)
        ).astype(int)

        # Observed consumption vs latent demand
        merged["observed_demand"] = merged["consumed_units"]
        # Use demand_units as true ground truth (if uncensored or for eval)
        merged["latent_demand"] = merged["demand_units"]

        return merged
