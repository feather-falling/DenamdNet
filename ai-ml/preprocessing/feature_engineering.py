import pandas as pd
from typing import Dict, Any, Tuple
from .load_data import DataLoader
from .validate_data import DataValidator
from .clean_data import DataCleaner
from .reconcile import StockReconciler
from .handle_missing import MissingDataHandler
from .time_split import TimeSplitter

class PreprocessingPipeline:
    """Master preprocessing pipeline ensuring schema compliance, reconciliation, and leak-free preparation."""

    def __init__(self, base_dir: str = "data"):
        self.loader = DataLoader(base_dir=base_dir)
        self.validator = DataValidator()
        self.cleaner = DataCleaner()
        self.reconciler = StockReconciler()
        self.missing_handler = MissingDataHandler()
        self.splitter = TimeSplitter()

    def process_country(self, country: str) -> Dict[str, Any]:
        """Loads and processes data for a single country."""
        cdata = self.loader.load_country_data(country)
        valid, errors = self.validator.validate(cdata)
        if not valid:
            raise ValueError(f"Data validation failed for {country}: {errors}")

        cleaned_demand = self.cleaner.clean_demand(cdata["demand"])
        cleaned_inventory = self.cleaner.clean_inventory(cdata["inventory"])
        cleaned_staff = self.cleaner.clean_staff(cdata["staff"])

        reconciled = self.reconciler.reconcile_and_flag_censoring(cleaned_inventory, cleaned_demand)
        grid = self.missing_handler.reindex_and_interpolate(reconciled)

        train_df, val_df, test_df = self.splitter.temporal_split(grid)

        return {
            "country": country,
            "full_grid": grid,
            "train": train_df,
            "val": val_df,
            "test": test_df,
            "medicines": cdata["medicines"],
            "phcs": cdata["phcs"],
            "events": cdata["events"],
            "neighbors": cdata["neighbors"]
        }
