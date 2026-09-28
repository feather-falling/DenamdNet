"""
Unit tests for Alert Processing, Priority Ordering, and Resource Filtering.
"""

from redistribution.engine.target_identifier import TargetIdentifier
from redistribution.engine.inventory_state import GlobalInventoryState


def test_alerts_processed_before_ordinary_predictions():
    """Verify that alert-driven targets are ordered before ordinary HIGH predictions."""
    alerts = [
        {
            "alert_id": "ALT-01",
            "country_code": "IN",
            "phc_id": "ALERT-PHC",
            "correlated_resources": ["Paracetamol"],
            "primary_driver": "Paracetamol"
        }
    ]
    predictions = [
        # Normal prediction: HIGH risk at ORDINARY-PHC
        {
            "phc_id": "ORDINARY-PHC",
            "medicine_id": "MED-001",
            "medicine_name": "Paracetamol",
            "country_code": "IN",
            "current_stock": 0.0,
            "forecast_demand": {"daily": 10.0, "planning_horizon_days": 7},
            "inventory_protection": {"safety_stock": 20.0},
            "risk": {"level": "HIGH"}
        },
        # Prediction for the ALERT-PHC: HIGH risk
        {
            "phc_id": "ALERT-PHC",
            "medicine_id": "MED-001",
            "medicine_name": "Paracetamol",
            "country_code": "IN",
            "current_stock": 0.0,
            "forecast_demand": {"daily": 20.0, "planning_horizon_days": 7},
            "inventory_protection": {"safety_stock": 20.0},
            "risk": {"level": "HIGH"}
        }
    ]

    state = GlobalInventoryState()
    targets = TargetIdentifier.identify_targets(alerts, predictions, state)

    assert len(targets) == 2
    # First target must be ALERT-PHC
    assert targets[0].phc_id == "ALERT-PHC"
    assert targets[0].is_alert_priority is True
    # Second target is ORDINARY-PHC
    assert targets[1].phc_id == "ORDINARY-PHC"
    assert targets[1].is_alert_priority is False


def test_resource_filtering_ignores_non_shortages():
    """Verify that correlated resources with surplus/healthy stock are NOT redistributed."""
    alerts = [
        {
            "alert_id": "ALT-01",
            "country_code": "IN",
            "phc_id": "ALERT-PHC",
            "correlated_resources": ["Paracetamol", "Metformin"],
            "primary_driver": "Paracetamol"
        }
    ]
    predictions = [
        # Paracetamol: in deficit, HIGH risk
        {
            "phc_id": "ALERT-PHC",
            "medicine_id": "MED-001",
            "medicine_name": "Paracetamol",
            "country_code": "IN",
            "current_stock": 0.0,
            "forecast_demand": {"daily": 20.0, "planning_horizon_days": 7},
            "inventory_protection": {"safety_stock": 20.0},
            "risk": {"level": "HIGH"}
        },
        # Metformin: healthy stock (5000 units), LOW risk
        {
            "phc_id": "ALERT-PHC",
            "medicine_id": "MED-002",
            "medicine_name": "Metformin",
            "country_code": "IN",
            "current_stock": 5000.0,
            "forecast_demand": {"daily": 10.0, "planning_horizon_days": 7},
            "inventory_protection": {"safety_stock": 20.0},
            "risk": {"level": "LOW"}
        }
    ]

    state = GlobalInventoryState()
    targets = TargetIdentifier.identify_targets(alerts, predictions, state)

    # Only Paracetamol should be a target; Metformin must be ignored because required == 0
    assert len(targets) == 1
    assert targets[0].medicine_id == "MED-001"
    assert targets[0].medicine_name == "Paracetamol"


def test_deduplication_of_alert_and_prediction():
    """If a medicine appears in both an alert and ordinary predictions, it must not be duplicated."""
    alerts = [
        {
            "alert_id": "ALT-01",
            "country_code": "IN",
            "phc_id": "PHC-1",
            "correlated_resources": ["Paracetamol"],
            "primary_driver": "Paracetamol"
        }
    ]
    predictions = [
        {
            "phc_id": "PHC-1",
            "medicine_id": "MED-001",
            "medicine_name": "Paracetamol",
            "country_code": "IN",
            "current_stock": 10.0,
            "forecast_demand": {"daily": 20.0, "planning_horizon_days": 7},
            "inventory_protection": {"safety_stock": 20.0},
            "risk": {"level": "HIGH"}
        }
    ]

    state = GlobalInventoryState()
    targets = TargetIdentifier.identify_targets(alerts, predictions, state)

    assert len(targets) == 1
    assert targets[0].is_alert_priority is True
