import pandas as pd
from typing import Dict, Any, List, Tuple

class DataValidator:
    """Validates structure, data types, and value constraints of raw datasets."""

    REQUIRED_DEMAND_COLS = ["date", "phc_id", "medicine_id", "demand_units", "patient_visits", "diagnostic_usage_units"]
    REQUIRED_INVENTORY_COLS = [
        "date", "phc_id", "medicine_id", "opening_stock", "received_units", 
        "consumed_units", "outgoing_transfer_units", "incoming_transfer_units", 
        "closing_stock", "unmet_demand_units"
    ]

    def validate_demand(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        for col in self.REQUIRED_DEMAND_COLS:
            if col not in df.columns:
                errors.append(f"Demand missing column: {col}")
        
        if df.isnull().sum().sum() > 0:
            errors.append(f"Demand contains null values: {df.isnull().sum().to_dict()}")

        if (df["demand_units"] < 0).any():
            errors.append("Demand contains negative demand_units")
            
        return len(errors) == 0, errors

    def validate_inventory(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        for col in self.REQUIRED_INVENTORY_COLS:
            if col not in df.columns:
                errors.append(f"Inventory missing column: {col}")

        if df.isnull().sum().sum() > 0:
            errors.append(f"Inventory contains null values: {df.isnull().sum().to_dict()}")

        if (df["closing_stock"] < 0).any():
            errors.append("Inventory contains negative closing_stock")

        return len(errors) == 0, errors

    def validate(self, country_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        d_ok, d_errs = self.validate_demand(country_data["demand"])
        i_ok, i_errs = self.validate_inventory(country_data["inventory"])
        all_errs = d_errs + i_errs
        return (d_ok and i_ok), all_errs

