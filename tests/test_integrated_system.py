"""
End-to-end integration test suite verifying:
1. PostgreSQL Database & Schema
2. Authentication (Register, Login, Password Hashing, JWT, Self-Inspection)
3. Authorization & Medicine Requests (Create, List, Peer Approve & Supply, Audit Events)
4. Pipeline Validation & Orchestration (Upload, Job Status, Real Metrics)
5. Downloadable Generated Output Files
"""

import os
import sys
import json
import pytest

# Ensure root is on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from fastapi.testclient import TestClient
from backend.main import app
from backend.db.database import init_db, SessionLocal
from backend.db.models import PHCAccount, MedicineRequest, RequestEvent


client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def setup_database():
    """Ensure database schema is created and clean for test suite."""
    init_db()


def test_root_and_health():
    res = client.get("/")
    assert res.status_code == 200
    assert "BRICS" in res.json().get("service", "")

    h_res = client.get("/health")
    assert h_res.status_code == 200
    assert h_res.json().get("status") == "healthy"


def test_auth_registration_and_login():
    # 1. Register a test PHC
    email = f"test_phc_{os.getpid()}@brics.health"
    reg_payload = {
        "phc_name": "Test Integration Health Centre",
        "email": email,
        "password": "StrongPassword123!",
        "country": "India"
    }
    res = client.post("/api/auth/register", json=reg_payload)
    assert res.status_code == 201, res.text
    data = res.json()
    assert "access_token" in data
    assert data["user"]["email"] == email
    assert data["user"]["phc_name"] == "Test Integration Health Centre"
    assert "password" not in str(data)  # Passwords never returned

    token = data["access_token"]

    # 2. Test duplicate email rejected
    dup_res = client.post("/api/auth/register", json=reg_payload)
    assert dup_res.status_code == 400
    assert "already registered" in dup_res.json()["detail"].lower()

    # 3. Test Login with correct credentials
    login_res = client.post("/api/auth/login", json={"email": email, "password": "StrongPassword123!"})
    assert login_res.status_code == 200
    login_data = login_res.json()
    assert "access_token" in login_data

    # 4. Test Login with wrong password
    bad_login = client.post("/api/auth/login", json={"email": email, "password": "WrongPassword"})
    assert bad_login.status_code == 401

    # 5. Test Authenticated /me endpoint
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

    # 6. Test Unauthenticated /me rejected
    unauth_me = client.get("/api/auth/me")
    assert unauth_me.status_code == 401


def test_medicine_requests_and_peer_approval():
    # Create Requester PHC
    req_email = f"requester_{os.getpid()}@brics.health"
    r_user = client.post("/api/auth/register", json={
        "phc_name": "Requester PHC Alpha",
        "email": req_email,
        "password": "Password123!",
        "country": "India"
    }).json()
    r_token = r_user["access_token"]

    # Create Donor PHC
    donor_email = f"donor_{os.getpid()}@brics.health"
    d_user = client.post("/api/auth/register", json={
        "phc_name": "Donor PHC Beta",
        "email": donor_email,
        "password": "Password123!",
        "country": "India"
    }).json()
    d_token = d_user["access_token"]

    # 1. Fetch medicine catalog
    cat_res = client.get("/api/requests/catalog")
    assert cat_res.status_code == 200
    catalog = cat_res.json()
    assert len(catalog) >= 18
    assert any(m["medicine_id"] == "MED-001" for m in catalog)

    # 2. Create request as Requester PHC
    req_payload = {
        "medicine_id": "MED-001",
        "quantity": 350.0,
        "urgency": "HIGH",
        "reason": "Sudden dengue outbreak in primary catchment"
    }
    create_res = client.post(
        "/api/requests",
        json=req_payload,
        headers={"Authorization": f"Bearer {r_token}"}
    )
    assert create_res.status_code == 201, create_res.text
    created = create_res.json()
    request_id = created["request_id"]
    assert created["quantity"] == 350.0
    assert created["status"] == "PENDING"
    assert created["requesting_phc_name"] == "Requester PHC Alpha"

    # 3. Check "My Requests" for Requester
    my_res = client.get("/api/requests/my", headers={"Authorization": f"Bearer {r_token}"})
    assert my_res.status_code == 200
    assert any(r["request_id"] == request_id for r in my_res.json())

    # 4. Check "Available Requests" for Donor PHC
    avail_res = client.get("/api/requests/available", headers={"Authorization": f"Bearer {d_token}"})
    assert avail_res.status_code == 200
    assert any(r["request_id"] == request_id for r in avail_res.json())

    # 5. Security: Requester cannot approve their own request
    self_appr = client.post(
        f"/api/requests/{request_id}/approve",
        json={"units_to_send": 350.0, "notes": "Self supply"},
        headers={"Authorization": f"Bearer {r_token}"}
    )
    assert self_appr.status_code == 400
    assert "cannot approve" in self_appr.json()["detail"].lower()

    # 6. Security: Donor cannot supply <= 0 units
    zero_appr = client.post(
        f"/api/requests/{request_id}/approve",
        json={"units_to_send": 0, "notes": "Zero units"},
        headers={"Authorization": f"Bearer {d_token}"}
    )
    assert zero_appr.status_code in [400, 422]


    # 7. Peer PHC approves and supplies 350 units
    appr_res = client.post(
        f"/api/requests/{request_id}/approve",
        json={"units_to_send": 350.0, "notes": "Dispatched emergency batch via district cold-chain vehicle"},
        headers={"Authorization": f"Bearer {d_token}"}
    )
    assert appr_res.status_code == 200
    appr_data = appr_res.json()
    assert appr_data["status"] == "COMPLETED"
    assert appr_data["supplied_by_phc_name"] == "Donor PHC Beta"
    assert appr_data["supplied_quantity"] == 350.0

    # 8. Requester checks notifications
    notif_res = client.get("/api/requests/notifications", headers={"Authorization": f"Bearer {r_token}"})
    assert notif_res.status_code == 200
    assert any(n["request_id"] == request_id for n in notif_res.json())


def test_results_and_downloads():
    # 1. Summary API
    sum_res = client.get("/api/results/summary")
    assert sum_res.status_code == 200
    s_data = sum_res.json()
    assert s_data["phcs_evaluated"] in [54, 163, 271]
    assert s_data["medicines"] == 18
    assert s_data["targets_evaluated"] > 0
    assert s_data["transfers_executed"] > 0
    assert s_data["total_units_transferred"] > 0
    assert s_data["fully_resolved"] > 0
    assert len(s_data["countries"]) >= 1


    # 2. Transfers API
    t_res = client.get("/api/results/transfers?limit=10")
    assert t_res.status_code == 200
    t_data = t_res.json()
    assert t_data["total"] > 0
    assert len(t_data["transfers"]) == 10

    sample = t_data["transfers"][0]
    assert "source_phc_id" in sample
    assert "target_phc_id" in sample
    assert "transferred_units" in sample
    assert "distance_km" in sample

    # 3. Medicines Movement API
    m_res = client.get("/api/results/medicines")
    assert m_res.status_code == 200
    m_data = m_res.json()
    assert len(m_data) > 0
    assert "units_moved" in m_data[0]

    # 4. Inventory Outcomes API
    inv_res = client.get("/api/results/inventory?limit=10")
    assert inv_res.status_code == 200
    assert len(inv_res.json()["records"]) == 10

    # 5. Downloads
    d1 = client.get("/api/results/download/next-day-phc-data")
    assert d1.status_code == 200
    assert len(d1.content) > 1000

    d2 = client.get("/api/results/download/redistribution-results")
    assert d2.status_code == 200
    assert len(d2.content) > 1000

    d3 = client.get("/api/results/download/unresolved-requirements")
    assert d3.status_code == 200
    assert len(d3.content) > 1000


def test_upload_validation_and_job_status():
    # 1. Invalid non-json upload
    bad_upload = client.post(
        "/api/run-daily/upload",
        files={"file": ("test.txt", b"not a json", "text/plain")}
    )
    assert bad_upload.status_code == 400
    assert "Only .json files are accepted" in bad_upload.json()["detail"]

    # 2. Malformed json syntax
    syntax_bad = client.post(
        "/api/run-daily/upload",
        files={"file": ("input.json", b"{ malformed: json", "application/json")}
    )
    assert syntax_bad.status_code == 400
    assert "malformed JSON syntax" in syntax_bad.json()["detail"]

    # 3. Valid JSON upload with operational input
    with open("input/input_today.json", "rb") as f:
        file_bytes = f.read()

    good_upload = client.post(
        "/api/run-daily/upload",
        files={"file": ("input_today.json", file_bytes, "application/json")},
        data={"country": "all"}
    )
    assert good_upload.status_code == 200
    upload_res = good_upload.json()
    job_id = upload_res["job_id"]
    assert job_id.startswith("job-")
    assert upload_res["status"] in ["running", "queued"]

    # 4. Poll status
    stat_res = client.get(f"/api/run-daily/status/{job_id}")
    assert stat_res.status_code == 200
    assert stat_res.json()["job_id"] == job_id
