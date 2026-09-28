"""
File loaders and country network resolution utilities.
"""

import os
import json
from typing import Dict, Any, List, Optional, Tuple


def normalize_country_name(country: str) -> str:
    """Normalizes country string or code to folder name ('india', 'brazil', 'south_africa', 'china', 'russia')."""
    c = str(country).strip().lower().replace(" ", "_").replace("-", "_")
    if c in ["india", "in"]:
        return "india"
    elif c in ["brazil", "br", "brasil"]:
        return "brazil"
    elif c in ["south_africa", "southafrica", "za", "sa"]:
        return "south_africa"
    elif c in ["china", "cn"]:
        return "china"
    elif c in ["russia", "ru", "russian_federation"]:
        return "russia"
    elif c in ["all", "global", "multi", "multicountry"]:
        return "all"
    return c


def country_to_iso_code(country: str) -> str:
    """Converts country name or code to standard 2-letter ISO code."""
    c = normalize_country_name(country)
    if c == "india":
        return "IN"
    elif c == "brazil":
        return "BR"
    elif c == "south_africa":
        return "ZA"
    elif c == "china":
        return "CN"
    elif c == "russia":
        return "RU"
    return c.upper()[:2]


def find_first_existing_file(candidate_paths: List[str]) -> Optional[str]:
    """Returns the first path from candidate_paths that exists on disk."""
    for p in candidate_paths:
        if p and os.path.exists(p):
            return p
    return None


def load_json_file(file_path: str) -> Any:
    """Loads JSON file with utf-8 encoding."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)


def load_static_network_data(base_dir: str, country: str) -> Dict[str, Any]:
    """Loads static master data for a country: phcs.json, medicines.json, nearest_neighbors.json."""
    country_norm = normalize_country_name(country)
    country_dir = os.path.join(base_dir, country_norm)
    if not os.path.exists(country_dir):
        raise FileNotFoundError(f"Static data directory for country '{country_norm}' not found: {country_dir}")

    # PHCs
    phc_path = os.path.join(country_dir, "phcs.json")
    phc_raw = load_json_file(phc_path)
    if isinstance(phc_raw, list):
        phcs = phc_raw
    elif isinstance(phc_raw, dict):
        phcs = phc_raw.get("phcs", [])
    else:
        phcs = []

    # Medicines
    med_path = os.path.join(country_dir, "medicines.json")
    med_raw = load_json_file(med_path)
    if isinstance(med_raw, list):
        medicines = med_raw
    elif isinstance(med_raw, dict):
        medicines = med_raw.get("medicines", [])
    else:
        medicines = []

    # Nearest Neighbors
    nn_path = os.path.join(country_dir, "nearest_neighbors.json")
    nn_raw = load_json_file(nn_path)
    if isinstance(nn_raw, dict) and "nearest_neighbors" in nn_raw:
        nearest_neighbors = nn_raw["nearest_neighbors"]
    elif isinstance(nn_raw, dict):
        nearest_neighbors = nn_raw
    else:
        nearest_neighbors = {}

    return {
        "country": country_norm,
        "country_code": country_to_iso_code(country_norm),
        "phcs": phcs,
        "medicines": medicines,
        "nearest_neighbors": nearest_neighbors
    }


def resolve_redistribution_input_files(
    alerts_path: Optional[str] = None,
    predictions_path: Optional[str] = None,
    input_today_path: Optional[str] = None
) -> Tuple[str, str, str]:
    """Resolves authoritative paths for alerts.json, predictions.json, and input_today.json,
    checking both output/ and outputs/ directories, and input/ and inputs/ directories.
    """
    # 1. Alerts path
    alerts_candidates = [
        alerts_path,
        os.path.join("output", "alerts", "alerts.json"),
        os.path.join("outputs", "alerts", "alerts.json"),
        os.path.join("output", "alerts.json"),
        os.path.join("outputs", "alerts.json")
    ]
    resolved_alerts = find_first_existing_file([p for p in alerts_candidates if p])
    if not resolved_alerts:
        raise FileNotFoundError(f"Disease outbreak alerts JSON not found in candidate paths: {alerts_candidates}")

    # 2. Predictions path
    preds_candidates = [
        predictions_path,
        os.path.join("output", "alerts", "predictions.json"),
        os.path.join("output", "predictions", "predictions.json"),
        os.path.join("outputs", "predictions", "predictions.json"),
        os.path.join("outputs", "alerts", "predictions.json"),
        os.path.join("output", "predictions.json"),
        os.path.join("outputs", "predictions.json")
    ]
    resolved_preds = find_first_existing_file([p for p in preds_candidates if p])
    if not resolved_preds:
        raise FileNotFoundError(f"Sharma predictions JSON not found in candidate paths: {preds_candidates}")

    # 3. Input today path
    input_candidates = [
        input_today_path,
        os.path.join("input", "input_today.json"),
        os.path.join("inputs", "input_today.json"),
        os.path.join("input", "daily_input_template.json"),
        os.path.join("inputs", "daily_input_template.json"),
        os.path.join("data", "daily_telemetry_input.json")
    ]
    resolved_input = find_first_existing_file([p for p in input_candidates if p])
    if not resolved_input:
        raise FileNotFoundError(f"Input today JSON not found in candidate paths: {input_candidates}")

    return resolved_alerts, resolved_preds, resolved_input
