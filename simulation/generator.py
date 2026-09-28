import os
import json
import random
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional, Tuple
import pandas as pd
import numpy as np


def normalize_country_name(country: str) -> str:
    """Normalizes country string to matching dataset folder name."""
    c = country.strip().lower().replace(" ", "_").replace("-", "_")
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
    return c


def load_json_catalog(file_path: str, entity_key: str) -> List[Dict[str, Any]]:
    """Loads a JSON catalog which might be a list or a dict with entity_key."""
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    elif isinstance(data, dict):
        return data.get(entity_key, [])
    return []


class DailyInputSimulator:
    """Generates complete daily operational input telemetry for EVERY PHC x EVERY MEDICINE.
    
    Adheres strictly to:
    1. Inventory conservation:
       closing_stock = opening_stock + received_units - consumed_units - outgoing_transfer_units + incoming_transfer_units
    2. Demand vs Consumption distinction:
       A PHC can demand more than it consumes if stock is insufficient.
    3. Event-driven simulation without data leakage:
       Events from data/<country>/events.json drive demand multipliers and patient visit surges,
       but NO event labels (cause_label, event_type, event_id) are placed in input_today.json.
    """

    def __init__(self, base_dir: str = "data"):
        self.base_dir = base_dir

    def load_network_metadata(self, country: str) -> Dict[str, Any]:
        """Loads static network metadata for the specified country."""
        country_norm = normalize_country_name(country)
        cdir = os.path.join(self.base_dir, country_norm)
        if not os.path.exists(cdir):
            raise FileNotFoundError(f"Country data directory not found: {cdir}")

        phcs = load_json_catalog(os.path.join(cdir, "phcs.json"), "phcs")
        medicines = load_json_catalog(os.path.join(cdir, "medicines.json"), "medicines")
        
        events_path = os.path.join(cdir, "events.json")
        events = []
        if os.path.exists(events_path):
            with open(events_path, "r", encoding="utf-8") as f:
                edata = json.load(f)
                events = edata if isinstance(edata, list) else edata.get("events", [])

        # Load recent inventory.csv if present to seed realistic opening stocks
        inv_path = os.path.join(cdir, "inventory.csv")
        recent_inv = None
        if os.path.exists(inv_path):
            try:
                # Read last 5000 rows to find latest closing stocks
                recent_inv = pd.read_csv(inv_path)
            except Exception:
                recent_inv = None

        return {
            "country": country_norm,
            "phcs": phcs,
            "medicines": medicines,
            "events": events,
            "recent_inventory": recent_inv
        }

    def get_active_events(self, events: List[Dict[str, Any]], target_date: str) -> List[Dict[str, Any]]:
        """Identifies events active on the target date."""
        active = []
        target_dt = pd.to_datetime(target_date)
        for evt in events:
            start_dt = pd.to_datetime(evt.get("start_date", "1970-01-01"))
            end_dt = pd.to_datetime(evt.get("end_date", "2099-12-31"))
            if start_dt <= target_dt <= end_dt:
                active.append(evt)
        return active

    def generate_daily_input(
        self,
        country: str = "india",
        date_str: Optional[str] = None,
        seed: Optional[int] = 42,
        stress_deficit_phc_count: int = 3
    ) -> Dict[str, Any]:
        """Generates a complete telemetry dictionary containing EVERY PHC x EVERY MEDICINE.
        
        Returns a dict strictly matching the input_today.json schema.
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)

        country_norm = normalize_country_name(country)
        meta = self.load_network_metadata(country_norm)
        phcs = meta["phcs"]
        medicines = meta["medicines"]
        all_events = meta["events"]
        recent_inv = meta["recent_inventory"]

        if not phcs:
            raise ValueError(f"No PHCs found in data/{country_norm}/phcs.json")
        if not medicines:
            raise ValueError(f"No medicines found in data/{country_norm}/medicines.json")

        if not date_str:
            date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        active_events = self.get_active_events(all_events, date_str)

        # Build lookup for latest closing stocks if available
        stock_lookup = {}
        if recent_inv is not None and not recent_inv.empty and "closing_stock" in recent_inv.columns:
            latest_inv = recent_inv.sort_values("date").groupby(["phc_id", "medicine_id"]).last().reset_index()
            for _, row in latest_inv.iterrows():
                stock_lookup[(str(row["phc_id"]), str(row["medicine_id"]))] = float(row["closing_stock"])

        # Determine which PHCs are under event stress
        event_affected_phc_ids = set()
        for evt in active_events:
            for p_id in evt.get("affected_phcs", []):
                event_affected_phc_ids.add(p_id)

        # If no active event or small affected set, select a few deficit stress PHCs for testing realistic alerts
        all_phc_ids = [p["phc_id"] for p in phcs]
        stress_candidates = [pid for pid in all_phc_ids if pid not in event_affected_phc_ids]
        deficit_phc_ids = set(random.sample(stress_candidates, min(stress_deficit_phc_count, len(stress_candidates))))

        records = []
        staff_attendance = []

        # Iterate over EVERY PHC
        for phc in phcs:
            phc_id = phc["phc_id"]
            is_event_phc = phc_id in event_affected_phc_ids
            is_deficit_phc = phc_id in deficit_phc_ids

            # Baseline patient visits
            capacity_opd = phc.get("capacity", {}).get("opd_capacity_per_day", 300)
            if is_event_phc:
                # Surge during active outbreak
                patient_visits = int(capacity_opd * random.uniform(1.8, 2.5))
            elif is_deficit_phc:
                patient_visits = int(capacity_opd * random.uniform(1.1, 1.4))
            else:
                patient_visits = max(50, int(capacity_opd * random.uniform(0.7, 1.1)))

            # Staff attendance from baseline
            staffing = phc.get("staffing_baseline", {})
            base_docs = staffing.get("doctors", 3)
            base_nurses = staffing.get("nurses", 6)
            base_pharma = staffing.get("pharmacists", 2)

            docs_present = max(1, int(round(base_docs * random.uniform(0.7, 1.0))))
            nurses_present = max(1, int(round(base_nurses * random.uniform(0.75, 1.0))))
            pharma_present = max(1, int(round(base_pharma * random.uniform(0.8, 1.0))))

            staff_attendance.append({
                "phc_id": phc_id,
                "doctors_present": docs_present,
                "nurses_present": nurses_present,
                "pharmacists_present": pharma_present
            })

            # Iterate over EVERY MEDICINE for this PHC
            for med in medicines:
                med_id = med["medicine_id"]
                med_category = str(med.get("category", "")).lower().replace(" ", "_")
                sim_profile = med.get("simulation_profile", {})
                base_scale = float(sim_profile.get("base_daily_demand_scale", 20.0))
                
                # If scale is fractional (like in Brazil/SA datasets where scale is ~1.0 multiplier), scale up to reasonable units
                if base_scale < 5.0:
                    base_daily = int(base_scale * 30.0)
                else:
                    base_daily = int(base_scale)

                # Check if this medicine is affected by an active event at this PHC
                multiplier = 1.0
                if is_event_phc:
                    for evt in active_events:
                        if phc_id in evt.get("affected_phcs", []):
                            evt_cats = [c.lower().replace(" ", "_") for c in evt.get("affected_categories", [])]
                            # Check match in category or substrings
                            category_match = any(
                                cat in med_category or med_category in cat
                                for cat in evt_cats
                            )
                            if category_match:
                                mult = float(evt.get("demand_multiplier", 3.0))
                                multiplier = max(multiplier, mult)

                # Calculate demand units
                if multiplier > 1.0:
                    demand_units = int(round(base_daily * multiplier * random.uniform(0.9, 1.2)))
                else:
                    # Normal daily demand fluctuation
                    demand_units = max(1, int(round(base_daily * random.uniform(0.8, 1.2))))

                # Diagnostic usage units
                diagnostic_usage = max(1, int(round(demand_units * random.uniform(0.15, 0.35))))

                # Determine opening stock
                cached_stock = stock_lookup.get((phc_id, med_id))
                if cached_stock is not None:
                    opening_stock = int(round(cached_stock))
                else:
                    # Generate realistic opening stock
                    if is_deficit_phc or (is_event_phc and multiplier > 1.0):
                        # Depleted stock for stressed PHCs to create HIGH risk / stockout condition
                        opening_stock = random.randint(0, max(5, int(demand_units * 0.6)))
                    else:
                        # Healthy stock for surplus facilities: 28 to 48 days worth
                        opening_stock = int(demand_units * random.uniform(28.0, 48.0))

                received_units = 0
                outgoing_transfer_units = 0
                incoming_transfer_units = 0

                # Available stock
                available_stock = opening_stock + received_units + incoming_transfer_units

                # Demand vs Consumption:
                # If stock is insufficient, PHC consumes what it has, but demand remains high
                consumed_units = min(demand_units, available_stock)

                # Closing stock strictly satisfies conservation equation
                closing_stock = (
                    opening_stock
                    + received_units
                    - consumed_units
                    - outgoing_transfer_units
                    + incoming_transfer_units
                )
                assert closing_stock >= 0, f"Negative closing stock generated: {closing_stock}"

                records.append({
                    "phc_id": phc_id,
                    "medicine_id": med_id,
                    "opening_stock": int(opening_stock),
                    "received_units": int(received_units),
                    "consumed_units": int(consumed_units),
                    "outgoing_transfer_units": int(outgoing_transfer_units),
                    "incoming_transfer_units": int(incoming_transfer_units),
                    "closing_stock": int(closing_stock),
                    "demand_units": int(demand_units),
                    "patient_visits": int(patient_visits),
                    "diagnostic_usage_units": int(diagnostic_usage)
                })

        return {
            "country": country_norm,
            "date": date_str,
            "simulation_notes": f"Simulated operational telemetry for {len(phcs)} PHCs x {len(medicines)} medicines ({len(records)} total records).",
            "records": records,
            "staff_attendance": staff_attendance
        }

    def generate_multicountry_scenario(
        self,
        target_date: str = "2026-10-02",
        seed: int = 42
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Generates a deliberate operational scenario spanning India, Brazil, and South Africa.
        
        Adheres strictly to the requested distributions across the 163 facilities:
        - Normal surplus: 60-70% (~64.4%)
        - Very high surplus: 10-20% (~16.6%)
        - Dengue-like pressure: ~10% (~9.8%)
        - Other pattern/event: ~10% (~9.8%)
        - Deficit facilities: 20-30% (~25.2%)
        
        Preserves inventory conservation, demand vs. consumption distinction, and leak-free inputs.
        """
        random.seed(seed)
        np.random.seed(seed)

        countries = ["india", "brazil", "south_africa", "china", "russia"]
        all_records = []
        all_staff = []

        phc_breakdown = {
            "normal_surplus": [],
            "very_high_surplus": [],
            "dengue_pattern": [],
            "other_pattern": [],
            "deficit": []
        }

        # Specific deliberate cluster assignments per country using authoritative PHC IDs
        country_assignments = {
            "india": {
                # 6 Dengue facilities (~11.1%)
                "dengue": [
                    "IN-DL-SWD-NJG-001", "IN-DL-SD-FPB-002", "IN-DL-SD-MEH-003",
                    "IN-DL-ND-ALP-004", "IN-UP-KNP-NBS-006", "IN-UP-LKO-IND-009"
                ],
                # 5 Other pattern facilities (~9.3%) (monsoon / diarrhoeal / respiratory)
                "other": [
                    "IN-AS-GHY-GNS-025", "IN-AS-GHY-JAL-026", "IN-WB-KOL-SLK-022",
                    "IN-WB-KOL-TLY-023", "IN-BR-PAT-KKB-019"
                ],
                # 9 Very high surplus facilities (~16.7%) (strong donors near urban centres)
                "very_high": [
                    "IN-DL-SWD-BJN-005", "IN-UP-KNP-JRL-007", "IN-UP-AGR-TJG-017",
                    "IN-MH-MUM-AND-027", "IN-KA-BLR-KOR-045", "IN-TN-CHN-ADY-048",
                    "IN-GJ-AMD-NRN-032", "IN-RJ-JAI-SNG-011", "IN-TG-HYD-KUK-043"
                ],
                # 13 Deficit facilities (~24.1%) (including severe outbreak depleted + delayed supply)
                "deficit": [
                    "IN-DL-SWD-NJG-001", "IN-DL-SD-FPB-002", "IN-DL-ND-ALP-004",
                    "IN-UP-KNP-NBS-006", "IN-AS-GHY-GNS-025", "IN-AS-GHY-JAL-026",
                    "IN-WB-KOL-SLK-022", "IN-MH-PUN-HAD-030", "IN-KA-BLR-YEL-046",
                    "IN-KL-TVM-PAT-052", "IN-OR-BBS-SHN-024", "IN-PB-ASR-RBT-014",
                    "IN-UK-DDN-CLN-018"
                ]
            },
            "brazil": {
                # 5 Dengue facilities (~9.3%)
                "dengue": [
                    "BR-SP-SAO-REP-001", "BR-SP-SAO-HEL-002", "BR-RJ-RIO-STM-004",
                    "BR-RJ-RIO-ROC-005", "BR-MG-BHO-CEN-007"
                ],
                # 6 Other pattern facilities (~11.1%) (respiratory / seasonal)
                "other": [
                    "BR-RS-POA-MOD-043", "BR-RS-POA-RES-044", "BR-PR-CWB-MAT-046",
                    "BR-SC-FLN-CEN-049", "BR-BA-SSA-PIT-013", "BR-PE-REC-BOA-016"
                ],
                # 9 Very high surplus facilities (~16.7%) (strong donors)
                "very_high": [
                    "BR-SP-SAO-PAR-003", "BR-SP-SAN-JAB-011", "BR-RJ-NIT-ICA-012",
                    "BR-MG-BHO-VEN-008", "BR-DF-BSB-CEI-035", "BR-GO-GYN-BUE-037",
                    "BR-AM-MAO-ALV-027", "BR-CE-FOR-MEI-018", "BR-PA-BEL-JUR-030"
                ],
                # 12 Deficit facilities (~22.2%)
                "deficit": [
                    "BR-SP-SAO-REP-001", "BR-SP-SAO-HEL-002", "BR-RJ-RIO-STM-004",
                    "BR-RJ-RIO-ROC-005", "BR-MG-BHO-CEN-007", "BR-RS-POA-MOD-043",
                    "BR-BA-SSA-PIT-013", "BR-AM-MAO-COM-028", "BR-PA-STM-ABA-025",
                    "BR-MA-SLZ-CEN-022", "BR-PI-THE-CEN-023", "BR-RN-NAT-PON-020"
                ]
            },
            "south_africa": {
                # 5 Acute Diarrhoeal / Outbreak facilities (~9.1%)
                "dengue": [
                    "ZA-GP-JHB-001", "ZA-GP-JHB-002", "ZA-GP-TSH-001",
                    "ZA-KZ-ETH-001", "ZA-WC-CPT-001"
                ],
                # 5 Other pattern facilities (~9.1%) (infectious / respiratory)
                "other": [
                    "ZA-WC-CPT-002", "ZA-EC-BUF-001", "ZA-EC-KSD-001",
                    "ZA-FS-MAN-001", "ZA-MP-EHL-001"
                ],
                # 9 Very high surplus facilities (~16.4%) (strong donors)
                "very_high": [
                    "ZA-GP-TSH-002", "ZA-WC-CPT-003", "ZA-KZ-ETH-002",
                    "ZA-FS-MAN-002", "ZA-LP-CAP-001", "ZA-NW-MAH-001",
                    "ZA-NC-KIM-001", "ZA-MP-EHL-002", "ZA-EC-NMB-001"
                ],
                # 13 Deficit facilities (~23.6%)
                "deficit": [
                    "ZA-GP-JHB-001", "ZA-GP-JHB-002", "ZA-GP-TSH-001",
                    "ZA-KZ-ETH-001", "ZA-WC-CPT-001", "ZA-WC-CPT-002",
                    "ZA-EC-BUF-001", "ZA-EC-KSD-001", "ZA-LP-VHE-001",
                    "ZA-NC-UPI-001", "ZA-NW-BOJ-001", "ZA-MP-NKANG-001",
                    "ZA-KZ-UGU-001"
                ]
            },
            "china": {
                # 5 Dengue / Pediatric surge facilities (~9.3%)
                "dengue": [
                    "CN-GD-CAN-TH-001", "CN-GD-CAN-YX-002", "CN-GD-CAN-HZ-003",
                    "CN-GD-SZX-FT-006", "CN-GD-SZX-NS-007"
                ],
                # 5 Other pattern facilities (~9.3%) (respiratory / seasonal)
                "other": [
                    "CN-BJ-BJS-CY-011", "CN-BJ-BJS-HD-012", "CN-BJ-BJS-DC-013",
                    "CN-BJ-BJS-XC-014", "CN-BJ-BJS-FT-015"
                ],
                # 9 Very high surplus facilities (~16.7%) (strong donors in major metro centers)
                "very_high": [
                    "CN-SH-SHA-HP-021", "CN-SH-SHA-JA-023", "CN-SH-SHA-PD-025",
                    "CN-SC-CTU-JJ-031", "CN-HB-WUH-JA-041", "CN-TJ-TJN-HP-047",
                    "CN-ZJ-HGH-XC-028", "CN-GD-CAN-PY-005", "CN-BJ-BJS-CP-018"
                ],
                # 13 Deficit facilities (~24.1%)
                "deficit": [
                    "CN-GD-CAN-TH-001", "CN-GD-CAN-YX-002", "CN-GD-SZX-FT-006",
                    "CN-BJ-BJS-CY-011", "CN-BJ-BJS-HD-012", "CN-HB-WUH-JH-042",
                    "CN-HB-WUH-WC-043", "CN-SC-CTU-WH-033", "CN-CQ-CKG-YZ-036",
                    "CN-SN-XAN-BL-039", "CN-SD-TNA-LX-051", "CN-ZJ-HGH-XC-028",
                    "CN-GD-FOS-CC-010"
                ]
            },
            "russia": {
                # 5 Acute outbreak / vector facilities (~9.3%)
                "dengue": [
                    "RU-MOW-CEN-001", "RU-MOW-ARB-002", "RU-MOW-BAS-003",
                    "RU-SPE-CEN-013", "RU-SPE-ADM-014"
                ],
                # 5 Other pattern facilities (~9.3%) (winter respiratory / cold snap)
                "other": [
                    "RU-SVE-YEK-LEN-026", "RU-SVE-YEK-KIR-027", "RU-NVS-NOV-CEN-032",
                    "RU-KDA-KRA-CEN-042", "RU-ROS-ROD-KIR-047"
                ],
                # 9 Very high surplus facilities (~16.7%) (strong regional donors)
                "very_high": [
                    "RU-MOW-ZAM-004", "RU-MOW-OST-008", "RU-SPE-PET-015",
                    "RU-SPE-VYB-017", "RU-TA-KAZ-VAS-037", "RU-NIZ-NIZ-NIZ-029",
                    "RU-SAM-SAM-LEN-035", "RU-BAS-UFA-KIR-049", "RU-PER-PER-LEN-052"
                ],
                # 13 Deficit facilities (~24.1%)
                "deficit": [
                    "RU-MOW-CEN-001", "RU-MOW-ARB-002", "RU-SPE-CEN-013",
                    "RU-SPE-ADM-014", "RU-SVE-YEK-LEN-026", "RU-NVS-NOV-CEN-032",
                    "RU-KDA-KRA-CEN-042", "RU-MOS-KHI-022", "RU-LEN-GAT-025",
                    "RU-CHY-CHE-CEN-039", "RU-OMK-OMS-CEN-044", "RU-VGG-VOL-CEN-050",
                    "RU-VOR-VOR-CEN-053"
                ]
            }
        }

        # Dengue relevant category substrings
        dengue_cat_keywords = [
            "analgesic", "rehydration", "fluid", "diagnostic", "consumable",
            "electrolytes", "pediatric"
        ]
        # Other pattern category keywords
        other_cat_keywords = [
            "antibacterial", "antibiotic", "antimalarial", "respiratory", "bronchodilator"
        ]

        total_phcs_all = 0
        total_meds_all = 0

        for country in countries:
            meta = self.load_network_metadata(country)
            phcs = meta["phcs"]
            medicines = meta["medicines"]
            total_phcs_all += len(phcs)
            total_meds_all += len(medicines)

            cfg = country_assignments[country]
            dengue_set = set(cfg["dengue"])
            other_set = set(cfg["other"])
            very_high_set = set(cfg["very_high"])
            deficit_set = set(cfg["deficit"])

            for phc in phcs:
                pid = phc["phc_id"]
                is_dengue = pid in dengue_set
                is_other = pid in other_set
                is_very_high = pid in very_high_set
                is_deficit = pid in deficit_set
                is_normal = not is_very_high and not is_deficit

                # Record category tracking
                if is_dengue:
                    phc_breakdown["dengue_pattern"].append(pid)
                if is_other:
                    phc_breakdown["other_pattern"].append(pid)
                if is_very_high:
                    phc_breakdown["very_high_surplus"].append(pid)
                if is_deficit:
                    phc_breakdown["deficit"].append(pid)
                if is_normal:
                    phc_breakdown["normal_surplus"].append(pid)

                # Patient visits and diagnostics
                opd_base = phc.get("capacity", {}).get("opd_capacity_per_day", 300)
                if is_dengue:
                    visits = int(opd_base * random.uniform(1.9, 2.5))
                elif is_other:
                    visits = int(opd_base * random.uniform(1.4, 1.8))
                elif is_deficit:
                    visits = int(opd_base * random.uniform(1.1, 1.3))
                else:
                    visits = max(60, int(opd_base * random.uniform(0.75, 1.05)))

                # Staff attendance
                sb = phc.get("staffing_baseline", {})
                all_staff.append({
                    "phc_id": pid,
                    "doctors_present": max(1, int(round(sb.get("doctors", 3) * random.uniform(0.75, 1.0)))),
                    "nurses_present": max(1, int(round(sb.get("nurses", 6) * random.uniform(0.8, 1.0)))),
                    "pharmacists_present": max(1, int(round(sb.get("pharmacists", 2) * random.uniform(0.8, 1.0))))
                })

                # Medicines
                for med in medicines:
                    mid = med["medicine_id"]
                    cat_str = str(med.get("category", "")).lower()
                    scale = float(med.get("simulation_profile", {}).get("base_daily_demand_scale", 20.0))
                    base_demand = int(scale if scale >= 5.0 else scale * 30.0)

                    # Determine event multiplier
                    mult = 1.0
                    if is_dengue and any(k in cat_str for k in dengue_cat_keywords):
                        mult = random.uniform(3.2, 4.0)
                    elif is_other and any(k in cat_str for k in other_cat_keywords):
                        mult = random.uniform(2.5, 3.5)

                    demand_units = max(1, int(round(base_demand * mult * random.uniform(0.9, 1.15))))
                    diag_units = max(1, int(round(demand_units * random.uniform(0.2, 0.4))))

                    # Opening stock allocation
                    if is_deficit:
                        # For deficit facilities: severely depleted stock for stressed or delayed items
                        if mult > 1.0 or random.random() < 0.70:
                            opening_stock = random.randint(0, max(2, int(demand_units * 0.15)))
                        else:
                            opening_stock = int(demand_units * random.uniform(1.5, 3.5))
                    elif is_very_high:
                        # Substantially more stock than protected requirement (strong donor)
                        # Scales relative to protected requirement (55 to 85 days), keeping robust minimum
                        scaled_vh = int(demand_units * random.uniform(55.0, 85.0))
                        opening_stock = max(scaled_vh, random.randint(4000, 7000))
                    else:
                        # Normal healthy surplus scaled to demand (28 to 48 days of demand)
                        # Guarantees meaningful moderate transferable surplus after deducting protected stock (~8-10 days)
                        opening_stock = int(demand_units * random.uniform(28.0, 48.0))

                    received = 0
                    out_tr = 0
                    in_tr = 0
                    available = opening_stock + received + in_tr

                    # Demand vs Consumption
                    consumed = min(demand_units, available)
                    closing = opening_stock + received - consumed - out_tr + in_tr
                    assert closing >= 0, f"Negative closing stock for {pid}, {mid}: {closing}"

                    all_records.append({
                        "phc_id": pid,
                        "medicine_id": mid,
                        "opening_stock": int(opening_stock),
                        "received_units": int(received),
                        "consumed_units": int(consumed),
                        "outgoing_transfer_units": int(out_tr),
                        "incoming_transfer_units": int(in_tr),
                        "closing_stock": int(closing),
                        "demand_units": int(demand_units),
                        "patient_visits": int(visits),
                        "diagnostic_usage_units": int(diag_units)
                    })

        total_phcs = total_phcs_all
        distribution_stats = {
            "total_phcs": total_phcs,
            "total_records": len(all_records),
            "total_staff": len(all_staff),
            "normal_surplus_count": len(phc_breakdown["normal_surplus"]),
            "normal_surplus_pct": round(len(phc_breakdown["normal_surplus"]) / total_phcs * 100, 1),
            "very_high_surplus_count": len(phc_breakdown["very_high_surplus"]),
            "very_high_surplus_pct": round(len(phc_breakdown["very_high_surplus"]) / total_phcs * 100, 1),
            "dengue_pattern_count": len(phc_breakdown["dengue_pattern"]),
            "dengue_pattern_pct": round(len(phc_breakdown["dengue_pattern"]) / total_phcs * 100, 1),
            "other_pattern_count": len(phc_breakdown["other_pattern"]),
            "other_pattern_pct": round(len(phc_breakdown["other_pattern"]) / total_phcs * 100, 1),
            "deficit_count": len(phc_breakdown["deficit"]),
            "deficit_pct": round(len(phc_breakdown["deficit"]) / total_phcs * 100, 1)
        }

        payload = {
            "country": "all",
            "date": target_date,
            "simulation_notes": f"Deliberate multi-country operational telemetry covering India (54), Brazil (54), South Africa (55), China (54), Russia (54). Total {len(all_records)} records.",
            "records": all_records,
            "staff_attendance": all_staff
        }

        return payload, distribution_stats

    def save_daily_input(
        self,
        telemetry: Dict[str, Any],
        output_paths: Optional[List[str]] = None
    ) -> List[str]:
        """Saves telemetry JSON to the designated output paths."""
        if not output_paths:
            output_paths = [
                os.path.join("input", "input_today.json"),
                os.path.join("inputs", "input_today.json")
            ]

        saved = []
        for p in output_paths:
            os.makedirs(os.path.dirname(os.path.abspath(p)), exist_ok=True)
            with open(p, "w", encoding="utf-8") as f:
                json.dump(telemetry, f, indent=2)
            saved.append(p)
        return saved

