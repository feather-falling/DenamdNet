# DATA AUDIT: BRICS Health Resilience Project

## 1. Dataset Overview & Scope
The existing data directory `data/` contains subdirectories for three countries:
- `data/india/`
- `data/brazil/`
- `data/south_africa/`

Each country directory contains a clean, internally consistent 1-year time-series dataset (October 1, 2025 to September 30, 2026 = 365 daily timesteps).

### Summary Statistics per Country
- **PHC Count**: 55 facilities per country (total 165 PHCs across 3 countries)
- **Medicine/Resource Count**: 18 essential items per country
- **Demand Records**: 361,350 rows (55 PHCs × 18 items × 365 days)
- **Inventory Records**: 361,350 rows
- **Staff Attendance Records**: ~78,000 - 100,000 rows
- **Missing Values**: 0 nulls across demand and inventory tables.

---

## 2. Table Specifications & Schemas

### `demand.csv`
- `date`: `YYYY-MM-DD` string (e.g. `2025-10-01`)
- `phc_id`: Facility code string (e.g. `IN-UP-MEE-001`, `BR-SP-RBP-001`, `ZA-GP-JHB-001`)
- `medicine_id`: Item code string (e.g. `MED-001` to `MED-018`)
- `demand_units`: Unconstrained healthcare demand count (integer/float)
- `patient_visits`: Daily OPD patient footfall at facility (integer)
- `diagnostic_usage_units`: Diagnostic test/kit utilization count (integer)
- `provenance`: Provenance tag (`SIMULATED`)

### `inventory.csv`
- `date`: `YYYY-MM-DD` string
- `phc_id`: Facility code string
- `medicine_id`: Item code string
- `opening_stock`: Start of day stock level (float)
- `received_units`: Inbound deliveries received during the day (float)
- `consumed_units`: Dispensed quantity (`min(demand, available)`) (float)
- `outgoing_transfer_units`: Stock transferred out to other PHCs (integer/float)
- `incoming_transfer_units`: Stock transferred in from other PHCs (integer/float)
- `closing_stock`: End of day stock level (`opening + received + incoming - consumed - outgoing`) (float)
- `unmet_demand_units`: Unfulfilled demand (`demand - consumed`) (float)
- `provenance`: Provenance tag (`SIMULATED`)

### `staff_attendance.csv`
- `date`: `YYYY-MM-DD` string
- `phc_id`: Facility code string
- `staff_category`: Category string (`doctors`, `nurses`, `pharmacists`, `lab_technicians`, `other_staff`)
- `scheduled_count`: Planned staff headcount (integer)
- `present_count`: Actual staff present (integer)
- `absence_rate`: Calculated absence ratio (`1 - present/scheduled`) (float)
- `provenance`: Provenance tag (`SIMULATED`)

### `medicines.json`
Catalog containing metadata for 18 medicines/resources per country:
- `medicine_id`: Unique item ID
- `name`: Full clinical item name
- `unit`: Unit of measurement (`tablets`, `vials`, `kits`, `doses`, `pieces`)
- `category`: Therapeutic / diagnostic category
- `simulation_profile`: Base daily demand scale & seasonality profile
- `provenance`: Provenance breakdown

### `phcs.json`
Metadata for 55 PHC facilities per country:
- `phc_id`, `name`, `official_name`, `country`, `state`, `district`, `city`, `facility_type`, `urban_rural`
- `geography`: `latitude`, `longitude`
- `catchment`: `population`
- `capacity`: `beds`, `opd_capacity_per_day`, `emergency_beds`
- `staffing_baseline`: `doctors`, `nurses`, `pharmacists`, `lab_technicians`
- `services`: Array of clinical services provided
- `infrastructure`: `cold_chain`, `pharmacy_storage`, `laboratory`

### `events.json` (Ground Truth ONLY)
Ground-truth simulation events describing stress events, epidemics, and surges:
- `event_id`, `event_type` (`EPIDEMIC_SURGE`, `SUPPLY_DISRUPTION`, etc.)
- `cause_label`: Descriptive cause (e.g. Dengue surge, Winter viral respiratory surge)
- `affected_phcs`: Array of affected PHC IDs
- `start_date`, `peak_date`, `end_date`, `intensity`, `affected_categories`, `demand_multiplier`
> **CRITICAL RULE**: `events.json` is strictly used for offline evaluation of anomaly and pattern detection performance. It is NEVER supplied as an operational feature input to any forecasting or detection model.

---

## 3. Data Integrity & Verification
- **Reconciliation**: Verified that `opening_stock + received_units + incoming_transfer_units - consumed_units - outgoing_transfer_units == closing_stock` holds across all records.
- **Censoring**: When `closing_stock == 0` or `unmet_demand_units > 0`, `consumed_units` is censored (lower bound of true demand).
- **Spatial Network**: Distance mappings are provided in `nearest_neighbors.json` for spatial feature computation.
