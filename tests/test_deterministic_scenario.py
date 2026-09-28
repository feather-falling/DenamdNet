"""
Required Deterministic End-to-End Test Scenarios (Section 41).
Strict verification of exact transfer quantities, protection invariant preservation, and status resolution.
"""

from redistribution.engine.inventory_state import GlobalInventoryState
from redistribution.engine.candidate_discovery import CandidateDiscovery
from redistribution.engine.distance_calculator import DistanceCalculator
from redistribution.engine.transfer_calculator import TransferCalculator
from redistribution.models.state import TargetRequirement


def test_deterministic_scenario_single_source():
    """Deterministic test scenario from Section 41:
    
    Target PHC:
      current stock = 0
      Daily forecast = 100
      Planning horizon = 7 days
      Safety stock = 300
      Required = 1000 (100 * 7 + 300 - 0 = 1000)

    Source A:
      current stock = 5000
      daily requirement = 100
      safety stock = 300
      Source protected = 1000 (100 * 7 + 300)
      Source transferable = 4000 (5000 - 1000)

    Expected:
      Target receives 1000.
      Source remains: 4000.
      Source remains above protected stock (4000 >= 1000).
      Target becomes protected (1000 >= 1000).
      Transfer status: RESOLVED.
    """
    state = GlobalInventoryState()

    # Setup Target PHC
    state.get_or_create(
        phc_id="TGT-PHC",
        medicine_id="MED-001",
        default_stock=0.0,
        daily_req=100.0,
        safety=300.0
    )

    # Setup Source A
    state.get_or_create(
        phc_id="SRC-A",
        medicine_id="MED-001",
        default_stock=5000.0,
        daily_req=100.0,
        safety=300.0
    )

    src_state = state.get("SRC-A", "MED-001")
    assert src_state.protected_stock == 1000.0
    assert src_state.transferable_surplus == 4000.0

    target_req = TargetRequirement(
        country_code="IN",
        phc_id="TGT-PHC",
        medicine_id="MED-001",
        medicine_name="Paracetamol 500 mg tablet",
        district="Test District",
        state_region="Test State",
        initial_stock=0.0,
        daily_forecast=100.0,
        safety_stock=300.0,
        planning_horizon_days=7,
        target_required_units=1000.0,
        remaining_requirement=1000.0
    )

    assert target_req.protected_target_stock == 1000.0
    assert target_req.target_required_units == 1000.0

    # Execute transfer
    transfer_record = TransferCalculator.execute_transfer(
        target=target_req,
        source_phc_id="SRC-A",
        distance_km=12.5,
        global_state=state
    )

    # Assertions
    assert transfer_record is not None
    assert transfer_record.transferred_units == 1000.0
    assert transfer_record.source_remaining_transferable_surplus == 3000.0
    assert transfer_record.remaining_target_requirement == 0.0
    assert transfer_record.status == "RESOLVED"

    # Source inventory verification
    assert src_state.current_stock == 4000.0
    assert src_state.current_stock >= src_state.protected_stock, "Source must remain above protected stock"
    assert src_state.outgoing_units == 1000.0

    # Target inventory verification
    tgt_state = state.get("TGT-PHC", "MED-001")
    assert tgt_state.current_stock == 1000.0
    assert tgt_state.current_stock >= tgt_state.protected_stock, "Target must become protected"
    assert tgt_state.incoming_units == 1000.0
    assert tgt_state.status == "RESOLVED"


def test_deterministic_scenario_multi_source():
    """Partial multi-source scenario from Section 41:
    
    Target requires: 5000
    Source A surplus: 3000
    Source B surplus: 2000

    Expected:
      A -> 3000
      B -> 2000
      Target -> RESOLVED
    """
    state = GlobalInventoryState()

    # Source A: protected=1000, current=4000 -> surplus=3000
    state.get_or_create(
        phc_id="SRC-A",
        medicine_id="MED-001",
        default_stock=4000.0,
        daily_req=100.0,
        safety=300.0
    )

    # Source B: protected=1000, current=3000 -> surplus=2000
    state.get_or_create(
        phc_id="SRC-B",
        medicine_id="MED-001",
        default_stock=3000.0,
        daily_req=100.0,
        safety=300.0
    )

    # Target: required 5000
    state.get_or_create(
        phc_id="TGT-PHC",
        medicine_id="MED-001",
        default_stock=0.0,
        daily_req=500.0,
        safety=1500.0
    )

    target_req = TargetRequirement(
        country_code="IN",
        phc_id="TGT-PHC",
        medicine_id="MED-001",
        medicine_name="Paracetamol 500 mg tablet",
        district="Test District",
        state_region="Test State",
        initial_stock=0.0,
        daily_forecast=500.0,
        safety_stock=1500.0,
        planning_horizon_days=7,
        target_required_units=5000.0,
        remaining_requirement=5000.0
    )

    # 1. Transfer from Source A
    t1 = TransferCalculator.execute_transfer(
        target=target_req,
        source_phc_id="SRC-A",
        distance_km=10.0,
        global_state=state
    )
    assert t1.transferred_units == 3000.0
    assert t1.status == "PARTIALLY_RESOLVED"
    assert target_req.remaining_requirement == 2000.0

    # 2. Transfer from Source B
    t2 = TransferCalculator.execute_transfer(
        target=target_req,
        source_phc_id="SRC-B",
        distance_km=25.0,
        global_state=state
    )
    assert t2.transferred_units == 2000.0
    assert t2.status == "RESOLVED"
    assert target_req.remaining_requirement == 0.0

    # Final state assertions
    tgt_state = state.get("TGT-PHC", "MED-001")
    assert tgt_state.current_stock == 5000.0
    assert tgt_state.status == "RESOLVED"

    assert state.get("SRC-A", "MED-001").current_stock == 1000.0  # At protected stock
    assert state.get("SRC-B", "MED-001").current_stock == 1000.0  # At protected stock
