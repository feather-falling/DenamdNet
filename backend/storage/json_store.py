"""
JSON-backed implementation of StorageInterface.
Provides thread-safe, resilient file storage for the operational backend.
"""

import os
import json
from typing import Dict, Any, List, Optional
from threading import Lock

from .interface import StorageInterface
from ..config import settings
from redistribution.utils.loaders import (
    find_first_existing_file,
    load_json_file,
    normalize_country_name,
    load_static_network_data
)


class JsonStorage(StorageInterface):
    """File-based JSON storage implementation of StorageInterface."""

    def __init__(self, base_dir: Optional[str] = None):
        self.base_dir = base_dir or settings.base_dir
        self.requests_file = settings.requests_storage_file
        self._lock = Lock()
        self._phc_cache: Dict[str, Dict[str, Any]] = {}
        self._load_all_phcs()

    def _load_all_phcs(self) -> None:
        """Loads and caches PHC metadata from all available country folders."""
        for cname in ["india", "brazil", "south_africa", "china", "russia"]:
            cdir = os.path.join(self.base_dir, cname)
            if os.path.exists(cdir):
                try:
                    data = load_static_network_data(self.base_dir, cname)
                    for phc in data.get("phcs", []):
                        pid = phc.get("phc_id")
                        if pid:
                            phc_copy = dict(phc)
                            phc_copy["country_name"] = cname
                            self._phc_cache[pid] = phc_copy
                except Exception:
                    pass

    def get_phc(self, phc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves PHC master metadata by facility ID."""
        if phc_id in self._phc_cache:
            return self._phc_cache[phc_id]
        # Refresh cache and check again
        self._load_all_phcs()
        return self._phc_cache.get(phc_id)

    def list_phcs(self, country: Optional[str] = None) -> List[Dict[str, Any]]:
        """Lists PHCs filtered optionally by country."""
        if not country:
            return list(self._phc_cache.values())
        c_norm = normalize_country_name(country)
        return [
            p for p in self._phc_cache.values()
            if normalize_country_name(p.get("country", p.get("country_name", ""))) == c_norm
        ]

    def get_phc_inventory(self, phc_id: str) -> List[Dict[str, Any]]:
        """Retrieves inventory for a specific PHC.
        Prioritizes post-redistribution state if available, otherwise prediction or input data.
        """
        # Try next_day_phc_data.json first
        next_day = self.get_next_day_phc_data()
        if next_day:
            items = [item for item in next_day if item.get("phc_id") == phc_id]
            if items:
                formatted = []
                for it in items:
                    formatted.append({
                        "medicine_id": it["medicine_id"],
                        "medicine_name": it.get("medicine_name", it["medicine_id"]),
                        "unit": it.get("unit", "units"),
                        "current_stock": it.get("final_stock", it.get("original_stock", 0.0)),
                        "daily_requirement": it.get("daily_requirement", 0.0),
                        "safety_stock": it.get("safety_stock", 0.0),
                        "protected_stock": it.get("protected_stock", 0.0),
                        "transferable_surplus": max(0.0, it.get("final_stock", 0.0) - it.get("protected_stock", 0.0)),
                        "remaining_requirement": it.get("remaining_requirement", 0.0),
                        "status": it.get("status", "HEALTHY")
                    })
                return formatted

        # Fallback to predictions.json
        preds = self.get_predictions(phc_id=phc_id)
        if preds:
            formatted = []
            for p in preds:
                curr_stock = float(p.get("current_stock", 0.0))
                daily = float(p.get("forecast_demand", {}).get("daily", 10.0))
                horizon = int(p.get("forecast_demand", {}).get("planning_horizon_days", 7))
                safety = float(p.get("inventory_protection", {}).get("safety_stock", 10.0))
                protected = (daily * horizon) + safety
                surplus = max(0.0, curr_stock - protected)
                shortage = max(0.0, protected - curr_stock)
                formatted.append({
                    "medicine_id": p["medicine_id"],
                    "medicine_name": p.get("medicine_name", p["medicine_id"]),
                    "unit": p.get("unit", "units"),
                    "current_stock": curr_stock,
                    "daily_requirement": daily,
                    "safety_stock": safety,
                    "protected_stock": protected,
                    "transferable_surplus": surplus,
                    "remaining_requirement": shortage,
                    "status": "HEALTHY" if curr_stock >= protected else "DEFICIT"
                })
            return formatted

        return []

    def get_predictions(
        self,
        phc_id: Optional[str] = None,
        medicine_id: Optional[str] = None,
        risk_level: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries prediction records with optional filters."""
        candidates = [
            os.path.join("output", "predictions", "predictions.json"),
            os.path.join("output", "alerts", "predictions.json"),
            os.path.join("outputs", "predictions", "predictions.json"),
            os.path.join("outputs", "alerts", "predictions.json")
        ]
        target_file = find_first_existing_file(candidates)
        if not target_file:
            return []

        try:
            records = load_json_file(target_file)
        except Exception:
            return []

        if not isinstance(records, list):
            return []

        results = []
        for r in records:
            if phc_id and r.get("phc_id") != phc_id:
                continue
            if medicine_id and r.get("medicine_id") != medicine_id:
                continue
            if risk_level and r.get("risk", {}).get("level", "").upper() != risk_level.upper():
                continue
            if country_code and r.get("country_code", "").upper() != country_code.upper():
                continue
            results.append(r)
        return results

    def get_alerts(
        self,
        phc_id: Optional[str] = None,
        district: Optional[str] = None,
        severity: Optional[str] = None,
        country_code: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Queries disease outbreak alerts with optional filters."""
        candidates = [
            os.path.join("output", "alerts", "alerts.json"),
            os.path.join("outputs", "alerts", "alerts.json")
        ]
        target_file = find_first_existing_file(candidates)
        if not target_file:
            return []

        try:
            alerts = load_json_file(target_file)
        except Exception:
            return []

        if not isinstance(alerts, list):
            return []

        results = []
        for a in alerts:
            if phc_id and a.get("phc_id") != phc_id:
                continue
            if district and a.get("district", "").lower() != district.lower():
                continue
            if severity and a.get("severity", "").upper() != severity.upper():
                continue
            if country_code and a.get("country_code", "").upper() != country_code.upper():
                continue
            results.append(a)
        return results

    def get_redistribution_results(self) -> Optional[Dict[str, Any]]:
        """Retrieves the latest redistribution run results."""
        candidates = [
            os.path.join("output", "redistribution", "redistribution_results.json"),
            os.path.join("outputs", "redistribution", "redistribution_results.json")
        ]
        target_file = find_first_existing_file(candidates)
        if not target_file:
            return None

        try:
            return load_json_file(target_file)
        except Exception:
            return None

    def get_next_day_phc_data(self) -> List[Dict[str, Any]]:
        """Retrieves the latest post-redistribution operational state."""
        candidates = [
            os.path.join("output", "redistribution", "next_day_phc_data.json"),
            os.path.join("outputs", "redistribution", "next_day_phc_data.json")
        ]
        target_file = find_first_existing_file(candidates)
        if not target_file:
            return []

        try:
            data = load_json_file(target_file)
            return data if isinstance(data, list) else []
        except Exception:
            return []

    # -------------------------------------------------------------------------
    # Operational Resource Requests Persistence
    # -------------------------------------------------------------------------
    def _read_requests_raw(self) -> Dict[str, Dict[str, Any]]:
        if not os.path.exists(self.requests_file):
            return {}
        try:
            with open(self.requests_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}

    def _write_requests_raw(self, requests: Dict[str, Dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(os.path.abspath(self.requests_file)), exist_ok=True)
        # Atomic write via temp file
        tmp_file = f"{self.requests_file}.tmp"
        with open(tmp_file, "w", encoding="utf-8") as f:
            json.dump(requests, f, indent=2)
        os.replace(tmp_file, self.requests_file)

    def save_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Saves a new PHC operational resource request."""
        with self._lock:
            requests = self._read_requests_raw()
            req_id = request_data["request_id"]
            requests[req_id] = request_data
            self._write_requests_raw(requests)
            return request_data

    def get_request(self, request_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves a resource request by unique request ID."""
        with self._lock:
            requests = self._read_requests_raw()
            return requests.get(request_id)

    def list_requests(
        self,
        phc_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Lists resource requests with optional filtering."""
        with self._lock:
            requests = self._read_requests_raw()
            result = list(requests.values())

        filtered = []
        for r in result:
            if phc_id and r.get("phc_id") != phc_id:
                continue
            if status and r.get("status", "").upper() != status.upper():
                continue
            filtered.append(r)
        # Sort by creation date descending
        filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return filtered

    def update_request(
        self,
        request_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Updates fields of an existing resource request."""
        with self._lock:
            requests = self._read_requests_raw()
            if request_id not in requests:
                return None
            req = requests[request_id]
            req.update(updates)
            self._write_requests_raw(requests)
            return req
