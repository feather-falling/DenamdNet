# South Africa Healthcare Resilience Dataset (1.0-seed)

## Overview
This dataset provides a 1-year historical operational baseline (365 days: `2025-10-01` to `2026-09-30`) for a network of 54 primary healthcare facilities (Community Health Centres & Primary Healthcare Clinics) across ~30 cities/municipalities in all 9 South African provinces.

The dataset is designed for health system supply chain resilience, demand forecasting, redistribution modeling, and emergency response analysis. It is structurally aligned with the India and Brazil Healthcare Resilience Datasets.

## Network Structure
- **Total Facilities**: 54
- **Provinces Covered**: Gauteng (GP), Western Cape (WC), Eastern Cape (EC), KwaZulu-Natal (KZN), Limpopo (LP), Mpumalanga (MP), Free State (FS), North West (NW), Northern Cape (NC).
- **Mandatory Seed Facilities Included**:
  1. `ZA-GP-JHB-001` — Chiawelo Community Health Centre (Johannesburg, GP)
  2. `ZA-GP-TSH-001` — Soshanguve Community Health Centre (Pretoria/Tshwane, GP)
  3. `ZA-EC-KSD-001` — Zithulele Gateway Clinic (Mqanduli / OR Tambo, EC)

## File Catalogue
1. `phcs.json` — Master registry of 54 South African facilities.
2. `medicines.json` — Standardized 18-item Primary Healthcare EML medicine & diagnostic catalogue.
3. `demand.csv` — Daily demand time-series (~354,780 records).
4. `inventory.csv` — Daily stock state enforcing conservation (`closing_stock = opening_stock + received - consumed - outgoing + incoming`).
5. `staff_attendance.csv` — Daily attendance for doctors, nurses, pharmacists, lab technicians, and support staff (~98,550 records).
6. `events.json` — Ground-truth synthetic stress events (Winter respiratory surge, Rural ART depot lag, Malaria seasonal peak, Central heatwave, Coastal floods, Festive holiday absence).
7. `nearest_neighbors.json` — Derived nearest-5 facilities per PHC (Haversine distance & travel time).
8. `provenance.json` — Provenance audit mapping.
9. `validation_report.json` — Automated verification status.

## Data Quality & Contracts
- **Inventory Conservation**: Verified across all 354,780 inventory records.
- **Referential Integrity**: 100% resolve across PHC, Medicine, and Event IDs.
- **Attendance Bounds**: `present_count <= scheduled_count` strictly enforced.
