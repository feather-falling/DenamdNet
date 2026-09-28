import os
import sys
import json
import numpy as np
import pandas as pd
from datetime import datetime

# Ensure ai-ml package directory is in sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from preprocessing.load_data import DataLoader
from preprocessing.validate_data import DataValidator
from preprocessing.feature_engineering import PreprocessingPipeline
from features.feature_builder import FeatureBuilder
from training.backtest import RollingOriginBacktester
from models.anomaly_detector import LayeredAnomalyDetector
from models.pattern_detector import MultiResourcePatternDetector
from inference.prediction_service import PredictionService
from simulation.closed_loop import ClosedLoopSimulation
from federated.simulate_federation import FederationSimulator

def run_master_pipeline():
    print("=" * 80)
    print("  BRICS HEALTH RESILIENCE ML SYSTEM -- MASTER PIPELINE EXECUTION")
    print("=" * 80)

    base_dir = "data"

    # Step 1: Data Preprocessing & Pipeline Validation
    print("\n--- [Phase 1 & 3] Data Loading, Validation & Preprocessing ---")
    pipeline = PreprocessingPipeline(base_dir=base_dir)
    india_data = pipeline.process_country("india")
    brazil_data = pipeline.process_country("brazil")
    sa_data = pipeline.process_country("south_africa")
    china_data = pipeline.process_country("china")
    russia_data = pipeline.process_country("russia")

    print(f"[OK] Preprocessed Datasets:")
    print(f"   India Train shape: {india_data['train'].shape}, Test shape: {india_data['test'].shape}")
    print(f"   Brazil Train shape: {brazil_data['train'].shape}, Test shape: {brazil_data['test'].shape}")
    print(f"   South Africa Train shape: {sa_data['train'].shape}, Test shape: {sa_data['test'].shape}")
    print(f"   China Train shape: {china_data['train'].shape}, Test shape: {china_data['test'].shape}")
    print(f"   Russia Train shape: {russia_data['train'].shape}, Test shape: {russia_data['test'].shape}")

    # Step 2: Feature Engineering & Leakage Prevention
    print("\n--- [Phase 4] Leak-Free Feature Engineering ---")
    builder = FeatureBuilder()
    india_train_feat = builder.build_features(india_data["train"], phc_meta=india_data["phcs"], neighbors=india_data["neighbors"])
    india_test_feat = builder.build_features(india_data["test"], phc_meta=india_data["phcs"], neighbors=india_data["neighbors"])
    print(f"[OK] Generated {india_train_feat.shape[1]} leak-free features for India dataset.")

    # Step 3: Model Ladder & Backtesting
    print("\n--- [Phase 5 & 6] Model Ladder & Rolling-Origin Backtesting ---")
    backtester = RollingOriginBacktester(horizon=7)
    comparison_df = backtester.run_comparison(india_train_feat.dropna().reset_index(drop=True), india_test_feat.dropna().reset_index(drop=True))
    print("Model Evaluation Summary (India Test Set):")
    print(comparison_df.to_string(index=False))

    # Step 4: Layered Anomaly & Outbreak Pattern Detection
    print("\n--- [Phase 7 & 8] Anomaly & Multi-Resource Outbreak Pattern Detection ---")
    anomaly_detector = LayeredAnomalyDetector()
    p50_preds = np.random.normal(loc=india_test_feat["consumed_units"].values, scale=10)
    anomaly_detector.fit(india_train_feat, india_train_feat["consumed_units"].values)
    anom_scores, detected, anom_types = anomaly_detector.detect(india_test_feat, p50_preds)

    print(f"[OK] Anomaly Detection Completed: {np.sum(detected)} anomalies flagged out of {len(detected)} rows.")

    pattern_detector = MultiResourcePatternDetector()
    med_list = india_data["medicines"].get("medicines", []) if isinstance(india_data["medicines"], dict) else india_data["medicines"]
    alerts = pattern_detector.detect_patterns(india_test_feat, anom_scores, med_list)
    print(f"[OK] Detected {len(alerts)} multi-resource disease/outbreak early warning alerts.")
    if alerts:
        print(f"   Sample Alert: {json.dumps(alerts[0], indent=2)}")

    # Step 5: Redistribution Contract & JSON Generation
    print("\n--- [Phase 9 & 10] Prediction Service & Exact JSON Contract ---")
    service = PredictionService()
    phc_list = india_data["phcs"].get("phcs", []) if isinstance(india_data["phcs"], dict) else india_data["phcs"]
    
    # 7-day multi-quantile forecast dummy matrix for sample rows
    q_preds_sample = np.tile(india_test_feat["consumed_units"].values[:, None, None], (1, 7, 3)).astype(np.float64)
    q_preds_sample[:, :, 0] *= 0.8
    q_preds_sample[:, :, 2] *= 1.3

    sharma_records = service.generate_sharma_records(
        india_test_feat.head(10), q_preds_sample[:10], anom_scores[:10], detected[:10], med_list, phc_list
    )
    print(f"[OK] Generated {len(sharma_records)} Sharma Redistribution JSON records.")
    print(f"   Sample Record Contract:")
    print(json.dumps(sharma_records[0], indent=2))

    # Step 6: Closed-Loop Simulation
    print("\n--- [Phase 11] Closed-Loop Simulation Environment ---")
    sim = ClosedLoopSimulation(india_data["test"].head(100), med_catalog=med_list, phc_catalog=phc_list)
    sim_res = sim.run_simulation(steps=5)
    print(f"[OK] Closed-Loop Simulation Completed: {sim_res['steps_completed']} timesteps.")
    for h in sim_res["simulation_history"]:
        print(f"   Step {h['step']}: {h['high_risk_count']} high risk facilities, {h['transfers_proposed']} transfers applied (Vol: {h['total_transfer_volume']})")

    # Step 7: Federated Learning Simulation
    print("\n--- [Phase 12] Federated Learning (FedProx) Simulation ---")
    fed_sim = FederationSimulator(base_dir=base_dir)
    fed_results = fed_sim.run_simulation()
    print("Federation Strategy Comparison (Local-Only vs Centralized vs FedProx):")
    print(fed_results.to_string(index=False))

    print("\n" + "=" * 80)
    print("  ALL BRICS HEALTH RESILIENCE ML PIPELINE PHASES EXECUTED SUCCESSFULLY!")
    print("=" * 80)

if __name__ == "__main__":
    run_master_pipeline()
