# Brazil Healthcare Resilience Dataset (1.0-seed)

## Overview
This dataset provides a 1-year historical operational baseline (365 days: `2025-10-01` to `2026-09-30`) for a network of 54 primary healthcare facilities (PHCs / UBS / Fluvial) across 30 cities in all 5 Brazilian macro-regions (North, Northeast, Central-West, Southeast, South).

The dataset is designed for health system supply chain resilience, demand forecasting, redistribution modeling, and emergency response analysis. It is structurally aligned with the India Healthcare Resilience Dataset.

## Network Structure
- **Total Facilities**: 54
- **Cities / Municipalities**: 30
- **Macro-Regions**: North, Northeast, Central-West, Southeast, South
- **Specialized Units**: Amazon Riverine Units (UBS Fluvial Abaré, UBS Fluvial Dra. Nilza Cordeiro, UBS Bailique) and Amazon Rural Units (UBS Rural de Portel).
- **Seed Facilities Included**:
  1. `BR-SP-SAO-REP-001` — UBS República (CNES 6090621) - São Paulo, SP
  2. `BR-RJ-RIO-STM-004` — Clínica da Família Santa Marta (CNES 6638421) - Rio de Janeiro, RJ
  3. `BR-BA-SSA-PIT-013` — UBS Pituba (CNES 2401836) - Salvador, BA
  4. `BR-PA-POR-RUR-024` — UBS Rural de Portel (CNES 2310100) - Portel, PA
  5. `BR-PA-STM-ABA-025` — UBS Fluvial Abaré (CNES 7128910) - Santarém / Tapajós, PA

## File Catalogue
1. `phcs.json` — Master registry of 54 facilities.
2. `medicines.json` — Standardized 18-item primary care medicine & diagnostic catalogue (SUS/RENAME).
3. `demand.csv` — Daily demand time-series (~354,780 records).
4. `inventory.csv` — Daily stock state enforcing conservation (`closing_stock = opening_stock + received - consumed - outgoing + incoming`).
5. `staff_attendance.csv` — Daily attendance for doctors, nurses, pharmacists, and lab technicians.
6. `events.json` — Ground-truth stress events (Dengue surge, Amazon waterway drought, Heatwave, Cold front, Monsoon floods, Carnival staff absence).
7. `nearest_neighbors.json` — Derived nearest-5 facilities per PHC (Haversine distance & travel time).
8. `provenance.json` — Provenance audit mapping.
9. `validation_report.json` — Automated verification status.

## Data Quality & Contracts
- **Inventory Conservation**: Verified across all 354,780 inventory records.
- **Referential Integrity**: 100% resolve across PHC, Medicine, and Event IDs.
- **Attendance Bounds**: `present_count <= scheduled_count` strictly enforced.
