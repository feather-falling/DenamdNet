# Russia Healthcare Resilience Dataset (1.0)

## Overview
This dataset provides a 1-year historical operational baseline (367 days: `2025-10-01` to `2026-10-02`) for a network of 54 City Polyclinics and primary care facilities (Городские поликлиники / ФАП) across major federal subjects of the Russian Federation (Moscow, Saint Petersburg, Moscow Oblast, Sverdlovsk, Novosibirsk, Tatarstan, Krasnodar, Nizhny Novgorod, and Primorsky Krai).

The dataset is designed for healthcare supply chain resilience, demand forecasting, disease outbreak detection, and peer redistribution modeling. It is 100% structurally aligned with the India, Brazil, and South Africa datasets.

## Network Structure
- **Total Facilities**: 54
- **Federal Subjects Covered**: Moscow, Saint Petersburg, Moscow Oblast, Sverdlovsk Oblast, Novosibirsk Oblast, Republic of Tatarstan, Krasnodar Krai, Nizhny Novgorod Oblast, Primorsky Krai
- **Facility Types**: City Polyclinics (Городские поликлиники)
- **Canonical Medicines**: 18 essential medicines & consumables (MED-001 to MED-018)

## File Catalogue
1. `phcs.json` — Master registry of 54 facilities.
2. `medicines.json` — Standardized 18-item primary care medicine & diagnostic catalogue with Russian localization.
3. `demand.csv` — Daily demand time-series (356,724 records).
4. `inventory.csv` — Daily stock state enforcing strict conservation (`closing_stock = opening_stock + received - consumed - outgoing + incoming`).
5. `staff_attendance.csv` — Daily attendance for doctors, nurses, pharmacists, and lab technicians.
6. `events.json` — Ground-truth public health pressure events (Winter respiratory/influenza wave, NW sub-zero cold wave, Ural-Siberian vector pressure, Black Sea summer gastroenteritis).
7. `nearest_neighbors.json` — Derived nearest facilities per PHC (Haversine distance & travel time).
8. `provenance.json` — Provenance audit mapping.
9. `validation_report.json` — Automated verification report.
