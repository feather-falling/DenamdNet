import os
import json
import pandas as pd
from typing import Dict, Any, Tuple

class DataLoader:
    """Loads raw healthcare data from data/<country>/ directory."""

    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir

    def load_country_data(self, country: str) -> Dict[str, Any]:
        """Loads all raw datasets and metadata for a specific country."""
        cdir = os.path.join(self.base_dir, country)
        if not os.path.exists(cdir):
            raise FileNotFoundError(f"Country directory not found: {cdir}")

        # Load CSVs
        demand_df = pd.read_csv(os.path.join(cdir, "demand.csv"))
        inventory_df = pd.read_csv(os.path.join(cdir, "inventory.csv"))
        
        staff_path = os.path.join(cdir, "staff_attendance.csv")
        staff_df = pd.read_csv(staff_path) if os.path.exists(staff_path) else pd.DataFrame()

        # Load JSONs
        with open(os.path.join(cdir, "medicines.json"), "r", encoding="utf-8") as f:
            medicines = json.load(f)

        with open(os.path.join(cdir, "phcs.json"), "r", encoding="utf-8") as f:
            phcs = json.load(f)

        events_path = os.path.join(cdir, "events.json")
        events = json.load(open(events_path, "r", encoding="utf-8")) if os.path.exists(events_path) else []

        neighbors_path = os.path.join(cdir, "nearest_neighbors.json")
        neighbors = json.load(open(neighbors_path, "r", encoding="utf-8")) if os.path.exists(neighbors_path) else {}

        prov_path = os.path.join(cdir, "provenance.json")
        provenance = json.load(open(prov_path, "r", encoding="utf-8")) if os.path.exists(prov_path) else {}

        return {
            "country": country,
            "demand": demand_df,
            "inventory": inventory_df,
            "staff": staff_df,
            "medicines": medicines,
            "phcs": phcs,
            "events": events,
            "neighbors": neighbors,
            "provenance": provenance
        }

    def load_all_countries(self, countries=None) -> Dict[str, Dict[str, Any]]:
        """Loads dataset for all specified countries."""
        if countries is None:
            countries = ["india", "brazil", "south_africa", "china", "russia"]
        return {country: self.load_country_data(country) for country in countries}
