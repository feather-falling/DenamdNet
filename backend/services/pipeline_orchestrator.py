"""
Daily Pipeline Orchestrator Service.
Coordinates the end-to-end operational workflow:
1. Input validation & storage (input/input_today.json)
2. Existing ML Demand Forecasting & Anomaly Detection (run_daily_prediction.py)
3. Existing Network Redistribution Engine (redistribution_engine.py)
4. Verification and dynamic results computation
5. Real-time background job tracking with accurate percentage stages
"""

import sys
import os
import json
import uuid
import shutil
import threading
import logging
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import HTTPException, status, UploadFile

logger = logging.getLogger(__name__)

# Ensure ai-ml and project root are on sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
AIML_DIR = os.path.join(PROJECT_ROOT, "ai-ml")
if AIML_DIR not in sys.path:
    sys.path.append(AIML_DIR)
if sys.path[0] != PROJECT_ROOT:
    sys.path.insert(0, PROJECT_ROOT)

OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output", "redistribution")
OUTPUTS_DIR = os.path.join(PROJECT_ROOT, "outputs")


class PipelineJob:
    def __init__(self, job_id: str, country: str = "all", input_file: str = "input/input_today.json"):
        self.job_id = job_id
        self.status = "queued"  # queued, running, completed, failed
        self.progress = 0  # 0, 17, 34, 52, 71, 86, 100
        self.stage = "Uploading input"
        self.country = country
        self.input_file = input_file
        self.created_at = datetime.now(timezone.utc).isoformat()
        self.updated_at = datetime.now(timezone.utc).isoformat()
        self.error: Optional[str] = None
        self.summary: Optional[Dict[str, Any]] = None

    def update(self, progress: int, stage: str, status: str = "running", error: Optional[str] = None):
        self.progress = progress
        self.stage = stage
        self.status = status
        self.error = error
        self.updated_at = datetime.now(timezone.utc).isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_id": self.job_id,
            "status": self.status,
            "progress": self.progress,
            "stage": self.stage,
            "country": self.country,
            "input_file": self.input_file,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "error": self.error,
            "summary": self.summary
        }


class PipelineOrchestrator:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PipelineOrchestrator, cls).__new__(cls)
                cls._instance._jobs: Dict[str, PipelineJob] = {}
                cls._instance._latest_job_id: Optional[str] = None
        return cls._instance

    @property
    def jobs(self) -> Dict[str, PipelineJob]:
        return self._jobs

    def validate_and_save_json(self, file_content: bytes, original_filename: str) -> str:
        """Validates uploaded input JSON and safely writes to input/input_today.json.
        Rejects path traversal, non-json files, corrupted syntax, or empty payloads.
        """
        # 1. Extension check
        if not original_filename.lower().endswith(".json"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input file. Only .json files are accepted."
            )

        # 2. Size check (max 60 MB)
        if len(file_content) > 60 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Input file too large. Maximum supported size is 60MB."
            )

        # 3. JSON parse check
        try:
            data = json.loads(file_content.decode("utf-8"))
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid input file: malformed JSON syntax ({str(e)})"
            )

        # 4. Structure validation
        if not isinstance(data, dict):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input file: root JSON must be an object with operational metadata and records."
            )

        records = data.get("records")
        if not isinstance(records, list) or len(records) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid input file: missing or empty 'records' array in operational telemetry."
            )

        # Quick schema check on first record
        sample = records[0]
        required_fields = ["phc_id", "medicine_id"]
        for rf in required_fields:
            if rf not in sample:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid input file: records must contain required field '{rf}'."
                )

        # 5. Safe write to input/input_today.json without modifying structure
        target_path = os.path.join(PROJECT_ROOT, "input", "input_today.json")
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        with open(target_path, "wb") as f:
            f.write(file_content)

        # Also sync to inputs/ folder for backward compatibility
        inputs_target = os.path.join(PROJECT_ROOT, "inputs", "input_today.json")
        os.makedirs(os.path.dirname(inputs_target), exist_ok=True)
        try:
            shutil.copyfile(target_path, inputs_target)
        except Exception:
            pass

        logger.info(f"Safely ingested {len(records)} operational records to {target_path}")
        return "input/input_today.json"

    def start_pipeline_job(self, country: str = "all", input_file: str = "input/input_today.json") -> PipelineJob:
        """Starts the daily ML forecasting & redistribution orchestration in a background thread."""
        job_id = f"job-{uuid.uuid4().hex[:8]}"
        job = PipelineJob(job_id=job_id, country=country, input_file=input_file)
        
        with self._lock:
            self._jobs[job_id] = job
            self._latest_job_id = job_id

        thread = threading.Thread(
            target=self._run_job_worker,
            args=(job,),
            daemon=True,
            name=f"Worker-{job_id}"
        )
        thread.start()
        return job

    def get_job(self, job_id: str) -> Optional[PipelineJob]:
        return self._jobs.get(job_id)

    def get_latest_job(self) -> Optional[PipelineJob]:
        if self._latest_job_id and self._latest_job_id in self._jobs:
            return self._jobs[self._latest_job_id]
        return None

    def _run_job_worker(self, job: PipelineJob):
        """Worker executing real ML and redistribution with progress stages."""
        logger.info(f"Starting execution of pipeline job {job.job_id}")

        try:
            # Stage 1: Validating operational data
            job.update(17, "Validating operational data", "running")
            input_full_path = os.path.join(PROJECT_ROOT, job.input_file)
            if not os.path.exists(input_full_path):
                raise FileNotFoundError(f"Input operational file not found at: {job.input_file}")

            # Stage 2: Running demand forecasting (Existing ML pipeline)
            job.update(34, "Running demand forecasting", "running")
            from run_daily_prediction import run_daily_prediction_pipeline

            # Stage 3: Detecting healthcare anomalies (alerts)
            job.update(52, "Detecting healthcare anomalies", "running")
            try:
                ml_result = run_daily_prediction_pipeline(
                    input_file=job.input_file,
                    country_override=job.country,
                    output_predictions_path="output/alerts/predictions.json",
                    output_alerts_path="output/alerts/alerts.json",
                    base_dir="data",
                    dry_run=True  # Keeps master historical CSVs clean while executing full multi-horizon model
                )
            except Exception as ml_err:
                logger.error(f"ML Pipeline Failure: {ml_err}", exc_info=True)
                job.update(job.progress, "Demand forecasting failed", "failed", error=f"Demand forecasting failed: {str(ml_err)}")
                return

            # Backward-compat sync
            os.makedirs(os.path.join(PROJECT_ROOT, "outputs", "alerts"), exist_ok=True)
            os.makedirs(os.path.join(PROJECT_ROOT, "outputs", "predictions"), exist_ok=True)
            shutil.copy(os.path.join(PROJECT_ROOT, "output/alerts/alerts.json"), os.path.join(PROJECT_ROOT, "outputs/alerts/alerts.json"))
            shutil.copy(os.path.join(PROJECT_ROOT, "output/alerts/predictions.json"), os.path.join(PROJECT_ROOT, "outputs/predictions/predictions.json"))

            # Stage 4: Finding redistribution sources & Executing transfers (Existing Redistribution Engine)
            job.update(71, "Finding redistribution sources & executing transfers", "running")
            from redistribution.engine.redistribution_engine import RedistributionEngine

            try:
                engine = RedistributionEngine(output_dir="output/redistribution")
                redis_result = engine.run(
                    country=job.country,
                    alerts_path="output/alerts/alerts.json",
                    predictions_path="output/alerts/predictions.json",
                    input_today_path=job.input_file,
                    save_outputs=True
                )
            except Exception as redis_err:
                logger.error(f"Redistribution Engine Failure: {redis_err}", exc_info=True)
                job.update(job.progress, "Redistribution processing failed", "failed", error=f"Redistribution processing failed: {str(redis_err)}")
                return

            # Stage 5: Generating next-day inventory & unresolved requirements
            job.update(86, "Generating next-day inventory & unresolved requirements", "running")

            # Verify expected output files exist
            f1 = os.path.join(OUTPUT_DIR, "next_day_phc_data.json")
            f2 = os.path.join(OUTPUT_DIR, "redistribution_results.json")
            f3 = os.path.join(OUTPUT_DIR, "unresolved_requirements.json")

            if not (os.path.exists(f1) and os.path.exists(f2) and os.path.exists(f3)):
                missing = [p for p in [f1, f2, f3] if not os.path.exists(p)]
                raise RuntimeError(f"Expected redistribution output files missing: {missing}")

            # Stage 6: Preparing dashboard & summary
            summary = self.calculate_summary_statistics()
            job.summary = summary
            job.update(100, "Dashboard results ready", "completed")
            logger.info(f"Pipeline job {job.job_id} completed successfully! 100%")

        except Exception as e:
            logger.error(f"Unexpected pipeline job crash: {e}", exc_info=True)
            job.update(job.progress, "Pipeline execution encountered an error", "failed", error=str(e))

    def calculate_summary_statistics(self) -> Dict[str, Any]:
        """Calculates dynamic top-level metrics, country statistics, and resolution counts from actual output files."""
        results_file = os.path.join(OUTPUT_DIR, "redistribution_results.json")
        next_day_file = os.path.join(OUTPUT_DIR, "next_day_phc_data.json")

        if not os.path.exists(results_file) or not os.path.exists(next_day_file):
            return {
                "phcs_evaluated": 0,
                "medicines": 0,
                "targets_evaluated": 0,
                "transfers_executed": 0,
                "total_units_transferred": 0,
                "fully_resolved": 0,
                "partially_resolved": 0,
                "execution_timestamp": datetime.now(timezone.utc).isoformat(),
                "countries": []
            }

        with open(results_file, "r", encoding="utf-8") as f:
            redis_data = json.load(f)
        with open(next_day_file, "r", encoding="utf-8") as f:
            next_day_data = json.load(f)

        raw_summary = redis_data.get("summary", {})
        transfers = redis_data.get("transfers", [])

        phcs = set(d.get("phc_id") for d in next_day_data if d.get("phc_id"))
        medicines = set(d.get("medicine_id") for d in next_day_data if d.get("medicine_id"))

        # Country mappings
        country_name_map = {
            "IN": "India",
            "BR": "Brazil",
            "ZA": "South Africa",
            "CN": "China",
            "RU": "Russia"
        }

        # Dynamic country aggregation
        country_codes = sorted(list(set(d.get("country_code", "UNKNOWN") for d in next_day_data if d.get("country_code"))))
        countries_stats = []

        for code in country_codes:
            c_name = country_name_map.get(code, code)
            c_phcs = set(d.get("phc_id") for d in next_day_data if d.get("country_code") == code)
            c_transfers = [t for t in transfers if t.get("target_phc_id", "").startswith(code)]
            c_targets = [d for d in next_day_data if d.get("country_code") == code and d.get("status") in ["RESOLVED", "PARTIALLY_RESOLVED", "UNRESOLVED"]]
            c_resolved = [t for t in c_transfers if t.get("status") == "RESOLVED"]
            c_units = sum(float(t.get("transferred_units", 0)) for t in c_transfers)

            countries_stats.append({
                "country": c_name,
                "country_code": code,
                "phcs_involved": len(c_phcs),
                "targets_evaluated": len(c_targets),
                "transfers_executed": len(c_transfers),
                "total_units_transferred": round(c_units, 1),
                "resolved_cases": len(c_resolved),
                "transfer_activity_rate": round((len(c_resolved) / max(1, len(c_targets))) * 100, 1)
            })

        return {
            "phcs_evaluated": len(phcs),
            "medicines": len(medicines),
            "targets_evaluated": raw_summary.get("total_targets_evaluated", len(transfers)),
            "transfers_executed": len(transfers),
            "total_units_transferred": round(raw_summary.get("total_volume_transferred", sum(float(t.get("transferred_units", 0)) for t in transfers)), 1),
            "fully_resolved": raw_summary.get("fully_resolved_count", len([t for t in transfers if t.get("status") == "RESOLVED"])),
            "partially_resolved": raw_summary.get("partially_resolved_count", 0),
            "execution_timestamp": raw_summary.get("execution_timestamp", datetime.now(timezone.utc).isoformat()),
            "countries": countries_stats
        }

    def get_transfers(
        self,
        search: Optional[str] = None,
        medicine_id: Optional[str] = None,
        country_code: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Queries actual transfer records from redistribution_results.json."""
        results_file = os.path.join(OUTPUT_DIR, "redistribution_results.json")
        if not os.path.exists(results_file):
            return {"total": 0, "transfers": []}

        with open(results_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        transfers = data.get("transfers", [])

        # Filter
        filtered = transfers
        if country_code:
            filtered = [t for t in filtered if t.get("target_phc_id", "").startswith(country_code.upper())]
        if medicine_id:
            filtered = [t for t in filtered if t.get("medicine_id") == medicine_id]
        if status_filter:
            filtered = [t for t in filtered if t.get("status") == status_filter.upper()]
        if search:
            q = search.lower().strip()
            filtered = [
                t for t in filtered
                if q in t.get("target_phc_id", "").lower()
                or q in t.get("source_phc_id", "").lower()
                or q in t.get("medicine_name", "").lower()
                or q in t.get("medicine_id", "").lower()
            ]

        total = len(filtered)
        paginated = filtered[offset: offset + limit]

        # Add unique id to each transfer for frontend keys
        for idx, t in enumerate(paginated):
            t["id"] = f"{t.get('source_phc_id')}_{t.get('target_phc_id')}_{t.get('medicine_id')}_{offset + idx}"

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "transfers": paginated
        }

    def get_medicine_movements(self) -> List[Dict[str, Any]]:
        """Calculates medicine-level transfer volumes and resolution counts from actual transfer output."""
        results_file = os.path.join(OUTPUT_DIR, "redistribution_results.json")
        if not os.path.exists(results_file):
            return []

        with open(results_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        transfers = data.get("transfers", [])
        med_stats: Dict[str, Dict[str, Any]] = {}

        for t in transfers:
            m_id = t.get("medicine_id", "UNKNOWN")
            m_name = t.get("medicine_name", m_id)
            units = float(t.get("transferred_units", 0))
            is_resolved = t.get("status") == "RESOLVED"

            if m_id not in med_stats:
                med_stats[m_id] = {
                    "medicine_id": m_id,
                    "medicine_name": m_name,
                    "transfers_count": 0,
                    "units_moved": 0.0,
                    "resolved_requirements": 0
                }

            med_stats[m_id]["transfers_count"] += 1
            med_stats[m_id]["units_moved"] += units
            if is_resolved:
                med_stats[m_id]["resolved_requirements"] += 1

        # Round and sort by units_moved desc
        result_list = list(med_stats.values())
        for m in result_list:
            m["units_moved"] = round(m["units_moved"], 1)

        result_list.sort(key=lambda x: x["units_moved"], reverse=True)
        return result_list

    def get_next_day_inventory(
        self,
        phc_id: Optional[str] = None,
        country_code: Optional[str] = None,
        status_filter: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Queries post-redistribution PHC inventory states from next_day_phc_data.json."""
        next_day_file = os.path.join(OUTPUT_DIR, "next_day_phc_data.json")
        if not os.path.exists(next_day_file):
            return {"total": 0, "records": []}

        with open(next_day_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        filtered = data
        if phc_id:
            filtered = [d for d in filtered if d.get("phc_id") == phc_id]
        if country_code:
            filtered = [d for d in filtered if d.get("country_code") == country_code.upper()]
        if status_filter:
            filtered = [d for d in filtered if d.get("status") == status_filter.upper()]

        total = len(filtered)
        paginated = filtered[offset: offset + limit]

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "records": paginated
        }


# Global singleton orchestrator
orchestrator = PipelineOrchestrator()
