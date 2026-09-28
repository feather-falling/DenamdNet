"""
Live verification script testing the running backend and database.
"""

import time
import requests

BASE = "http://127.0.0.1:8000"

print("1. Testing Health & Root...")
r = requests.get(f"{BASE}/")
assert r.status_code == 200
print("   Root OK:", r.json())

print("\n2. Testing Trigger Daily Pipeline...")
r = requests.post(f"{BASE}/api/run-daily", json={"country": "all", "input_file": "input/input_today.json"})
assert r.status_code == 200
job = r.json()
job_id = job["job_id"]
print(f"   Job {job_id} launched: {job['status']} ({job['progress']}%)")

print("\n3. Polling Real-Time Pipeline Progress...")
for _ in range(60):
    time.sleep(2)
    s = requests.get(f"{BASE}/api/run-daily/status/{job_id}").json()
    print(f"   Progress: {s['progress']}% | Stage: {s['stage']} | Status: {s['status']}")
    if s["status"] in ["completed", "failed"]:
        assert s["status"] == "completed", f"Job failed: {s.get('error')}"
        break

print("\n4. Verifying Results Summary (Multi-Country Dynamic Metrics)...")
summary = requests.get(f"{BASE}/api/results/summary").json()
print("   PHCs Evaluated:", summary["phcs_evaluated"])
print("   Medicines Count:", summary["medicines"])
print("   Targets Evaluated:", summary["targets_evaluated"])
print("   Transfers Executed:", summary["transfers_executed"])
print("   Total Volume Transferred:", summary["total_units_transferred"])
print("   Fully Resolved:", summary["fully_resolved"])
print("   Partially Resolved:", summary["partially_resolved"])
print("   Countries:", [c["country"] for c in summary["countries"]])
assert summary["phcs_evaluated"] == 163
assert summary["medicines"] == 18
assert summary["transfers_executed"] == 1075
assert summary["fully_resolved"] == 874

print("\n5. Testing PHC Registration & Login in PostgreSQL...")
email = f"live_delhi_{int(time.time())}@brics.health"
reg_resp = requests.post(f"{BASE}/api/auth/register", json={
    "phc_name": "Delhi Central Health Center",
    "email": email,
    "password": "SecurePassword123!",
    "country": "India"
})
assert reg_resp.status_code == 201
reg_data = reg_resp.json()
token = reg_data["access_token"]
print(f"   Registered PHC: {reg_data['user']['phc_name']} ({reg_data['user']['assigned_phc_id']})")

print("\n6. Submitting Medicine Request...")
req_resp = requests.post(
    f"{BASE}/api/requests",
    json={
        "medicine_id": "MED-001",
        "quantity": 500,
        "urgency": "HIGH",
        "reason": "Dengue outbreak spike requires extra paracetamol"
    },
    headers={"Authorization": f"Bearer {token}"}
)
assert req_resp.status_code == 201
req_data = req_resp.json()
req_id = req_data["request_id"]
print(f"   Created Request {req_id}: {req_data['quantity']} units of {req_data['medicine_name']} (Status: {req_data['status']})")

print("\n7. Registering Donor PHC & Approving Request...")
donor_email = f"live_bangalore_{int(time.time())}@brics.health"
d_resp = requests.post(f"{BASE}/api/auth/register", json={
    "phc_name": "Bangalore Community Dispensary",
    "email": donor_email,
    "password": "SecurePassword123!",
    "country": "India"
})
d_token = d_resp.json()["access_token"]

# Donor approves & supplies
appr_resp = requests.post(
    f"{BASE}/api/requests/{req_id}/approve",
    json={"units_to_send": 500, "notes": "Approved from regional buffer stock."},
    headers={"Authorization": f"Bearer {d_token}"}
)
assert appr_resp.status_code == 200
appr_data = appr_resp.json()
print(f"   Request {req_id} Approved! Status: {appr_data['status']}, Supplied By: {appr_data['supplied_by_phc_name']} ({appr_data['supplied_quantity']} units)")

print("\n8. Requester Views Updated Status...")
my_reqs = requests.get(f"{BASE}/api/requests/my", headers={"Authorization": f"Bearer {token}"}).json()
my_req = next(r for r in my_reqs if r["request_id"] == req_id)
assert my_req["status"] == "COMPLETED"
assert my_req["supplied_by_phc_name"] == "Bangalore Community Dispensary"
print(f"   Requester confirmed update: Status = {my_req['status']}, Supplier = {my_req['supplied_by_phc_name']}")

print("\n[ALL LIVE VERIFICATIONS PASSED SUCCESSFULLY]")
