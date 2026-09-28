"""
API and Backend integration tests using FastAPI TestClient.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_health_endpoint():
    """Verify GET /health returns 200 and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_predictions_endpoint():
    """Verify GET /api/predictions returns predictions with query filtering."""
    response = client.get("/api/predictions")
    assert response.status_code == 200
    data = response.json()
    assert "total_records" in data
    assert "records" in data

    # Test filtering by risk level
    high_resp = client.get("/api/predictions?risk_level=HIGH")
    assert high_resp.status_code == 200
    high_data = high_resp.json()
    for rec in high_data["records"]:
        assert rec["risk"]["level"] == "HIGH"


def test_alerts_endpoint():
    """Verify GET /api/alerts returns alert records with severity filtering."""
    response = client.get("/api/alerts")
    assert response.status_code == 200
    data = response.json()
    assert "total_alerts" in data
    assert "alerts" in data

    # Test filtering by severity
    em_resp = client.get("/api/alerts?severity=EMERGENCY")
    assert em_resp.status_code == 200
    for a in em_resp.json()["alerts"]:
        assert a["severity"] == "EMERGENCY"


def test_phc_metadata_and_inventory():
    """Verify GET /api/phcs/{phc_id} and GET /api/phcs/{phc_id}/inventory."""
    phc_id = "IN-DL-SWD-NJG-001"
    phc_resp = client.get(f"/api/phcs/{phc_id}")
    assert phc_resp.status_code == 200
    phc_data = phc_resp.json()
    assert phc_data["phc_id"] == phc_id
    assert "name" in phc_data

    # Inventory
    inv_resp = client.get(f"/api/phcs/{phc_id}/inventory")
    assert inv_resp.status_code == 200
    inv_data = inv_resp.json()
    assert inv_data["phc_id"] == phc_id
    assert "inventory" in inv_data
    assert len(inv_data["inventory"]) > 0


def test_redistribution_status_and_run():
    """Verify POST /api/redistribution/run and GET /api/redistribution/results."""
    run_resp = client.post("/api/redistribution/run", json={"country": "india"})
    assert run_resp.status_code == 200
    run_data = run_resp.json()
    assert run_data["status"] == "COMPLETED"

    # Status
    status_resp = client.get("/api/redistribution/status")
    assert status_resp.status_code == 200
    assert status_resp.json()["status"] == "COMPLETED"

    # Results
    res_resp = client.get("/api/redistribution/results")
    assert res_resp.status_code == 200
    res_data = res_resp.json()
    assert "summary" in res_data
    assert "transfers" in res_data


def test_operational_request_lifecycle():
    """Verify request lifecycle: PENDING -> ACCEPTED -> COMPLETED, plus cancellation."""
    # 1. Create request
    create_payload = {
        "phc_id": "IN-DL-SWD-NJG-001",
        "medicine_id": "MED-001",
        "quantity": 150.0,
        "urgency": "HIGH",
        "required_by": "2026-10-05",
        "reason": "Dengue outbreak spike requires extra paracetamol"
    }
    create_resp = client.post("/api/requests", json=create_payload)
    assert create_resp.status_code == 201
    created_req = create_resp.json()
    req_id = created_req["request_id"]
    assert created_req["status"] == "PENDING"
    assert created_req["quantity"] == 150.0

    # 2. Get request by ID
    get_resp = client.get(f"/api/requests/{req_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["request_id"] == req_id

    # 3. Accept request
    accept_resp = client.post(
        f"/api/requests/{req_id}/accept",
        json={"source_phc_id": "IN-DL-SWD-BJN-005", "notes": "Approved by district pharmacy"}
    )
    assert accept_resp.status_code == 200
    assert accept_resp.json()["status"] == "ACCEPTED"
    assert accept_resp.json()["accepted_by_phc_id"] == "IN-DL-SWD-BJN-005"

    # 4. Complete request
    complete_resp = client.post(
        f"/api/requests/{req_id}/complete",
        json={"notes": "Physical batch delivered"}
    )
    assert complete_resp.status_code == 200
    assert complete_resp.json()["status"] == "COMPLETED"

    # 5. Test Cancel on another request
    create_payload2 = {
        "phc_id": "IN-DL-SWD-NJG-001",
        "medicine_id": "MED-002",
        "quantity": 50.0,
        "urgency": "MEDIUM",
        "required_by": "2026-10-06",
        "reason": "Temporary buffer"
    }
    resp2 = client.post("/api/requests", json=create_payload2)
    req_id2 = resp2.json()["request_id"]

    cancel_resp = client.post(f"/api/requests/{req_id2}/cancel", json={"notes": "No longer needed"})
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["status"] == "CANCELLED"


def test_validation_errors():
    """Verify input validation for invalid requests."""
    # Negative quantity
    invalid_payload = {
        "phc_id": "IN-DL-SWD-NJG-001",
        "medicine_id": "MED-001",
        "quantity": -50.0,
        "urgency": "HIGH",
        "required_by": "2026-10-05",
        "reason": "Test negative"
    }
    resp = client.post("/api/requests", json=invalid_payload)
    assert resp.status_code == 422

    # Non-existent PHC
    bad_phc = client.get("/api/phcs/NON_EXISTENT_PHC_999")
    assert bad_phc.status_code == 404
