import numpy as np
import pandas as pd
from typing import Dict, Any, List

class InventorySimulator:
    """Manages PHC inventory state, transfers, consumption, and daily progression."""

    def __init__(self, initial_df: pd.DataFrame):
        self.state_df = initial_df.copy()

    def apply_transfers(self, transfers: List[Dict[str, Any]]):
        """Applies stock transfers between PHCs:
        transfer = {'source_phc': ..., 'dest_phc': ..., 'medicine_id': ..., 'quantity': ...}
        Modifies inventory: source stock decreases, dest stock increases.
        Does NOT alter disease demand.
        """
        for t in transfers:
            src = t["source_phc"]
            dst = t["dest_phc"]
            m_id = t["medicine_id"]
            qty = float(t["quantity"])

            src_mask = (self.state_df["phc_id"] == src) & (self.state_df["medicine_id"] == m_id)
            if src_mask.any():
                self.state_df.loc[src_mask, "closing_stock"] = np.maximum(0, self.state_df.loc[src_mask, "closing_stock"] - qty)
                self.state_df.loc[src_mask, "outgoing_transfer_units"] = self.state_df.loc[src_mask, "outgoing_transfer_units"] + qty

            dst_mask = (self.state_df["phc_id"] == dst) & (self.state_df["medicine_id"] == m_id)
            if dst_mask.any():
                self.state_df.loc[dst_mask, "closing_stock"] = self.state_df.loc[dst_mask, "closing_stock"] + qty
                self.state_df.loc[dst_mask, "incoming_transfer_units"] = self.state_df.loc[dst_mask, "incoming_transfer_units"] + qty

    def step_next_day(self, next_day_demand_df: pd.DataFrame) -> pd.DataFrame:
        """Advances simulation to next timestep. Updates opening stock from previous closing stock."""
        prev_closing = self.state_df.groupby(["phc_id", "medicine_id"])["closing_stock"].last().reset_index().rename(columns={"closing_stock": "new_opening"})

        next_state = pd.merge(next_day_demand_df, prev_closing, on=["phc_id", "medicine_id"], how="left")
        next_state["opening_stock"] = next_state["new_opening"].fillna(next_state["opening_stock"])
        next_state.drop(columns=["new_opening"], inplace=True)

        available = next_state["opening_stock"] + next_state.get("received_units", 0) + next_state.get("incoming_transfer_units", 0)
        dem = next_state.get("demand_units", next_state.get("consumed_units", 0))

        next_state["consumed_units"] = np.minimum(dem, available)
        next_state["unmet_demand_units"] = np.maximum(0, dem - available)
        next_state["closing_stock"] = available - next_state["consumed_units"] - next_state.get("outgoing_transfer_units", 0)

        self.state_df = next_state.copy()
        return self.state_df
