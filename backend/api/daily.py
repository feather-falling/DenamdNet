"""
Daily Orchestration API Endpoints.
Supports:
1. Upload today's JSON (input_today.json) with strict validation & auto-orchestration
2. Triggering the daily pipeline with job ID tracking
3. Polling real-time job status and progress (0% -> 17% -> 34% -> 52% -> 71% -> 86% -> 100%)
"""

import os
from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, status
from pydantic import BaseModel
from ..services.pipeline_orchestrator import orchestrator

router = APIRouter(prefix="/api/run-daily", tags=["Daily Orchestration"])


class RunDailyRequest(BaseModel):
    country: Optional[str] = "all"
    input_file: Optional[str] = "input/input_today.json"


@router.post("/upload", response_model=Dict[str, Any])
async def upload_and_run_daily(
    file: UploadFile = File(...),
    country: Optional[str] = Form("all")
) -> Dict[str, Any]:
    """Accepts input_today.json upload, validates content, saves to input/input_today.json,
    and automatically starts the real ML & redistribution pipeline.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input file. No filename provided."
        )

    content = await file.read()
    saved_path = orchestrator.validate_and_save_json(content, file.filename)

    # Start the daily orchestration job
    job = orchestrator.start_pipeline_job(country=country or "all", input_file=saved_path)

    return {
        "message": "Input telemetry accepted. Operational analysis started.",
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "stage": job.stage,
        "saved_path": saved_path
    }


@router.post("", response_model=Dict[str, Any])
def run_daily_pipeline(payload: Optional[RunDailyRequest] = None) -> Dict[str, Any]:
    """Triggers the daily pipeline on an existing input file and returns a trackable job ID."""
    country = payload.country if payload and payload.country else "all"
    input_file = payload.input_file if payload and payload.input_file else "input/input_today.json"

    # Verify input file exists
    if not os.path.exists(input_file):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Input operational file '{input_file}' not found. Please upload input_today.json first."
        )

    job = orchestrator.start_pipeline_job(country=country, input_file=input_file)

    return {
        "job_id": job.job_id,
        "status": job.status,
        "progress": job.progress,
        "stage": job.stage,
        "country": job.country
    }


@router.get("/status/{job_id}", response_model=Dict[str, Any])
def get_job_status(job_id: str) -> Dict[str, Any]:
    """Returns the real-time progress and stage of a pipeline execution job."""
    job = orchestrator.get_job(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Job '{job_id}' not found."
        )
    return job.to_dict()


@router.get("/latest", response_model=Dict[str, Any])
def get_latest_job_status() -> Dict[str, Any]:
    """Returns the latest pipeline run status, or calculates summary of current output state."""
    job = orchestrator.get_latest_job()
    if job:
        return job.to_dict()

    # If no job was run during this backend process session, return completed state based on files
    summary = orchestrator.calculate_summary_statistics()
    return {
        "job_id": "latest-cached",
        "status": "completed" if summary.get("transfers_executed", 0) > 0 else "idle",
        "progress": 100 if summary.get("transfers_executed", 0) > 0 else 0,
        "stage": "Dashboard results ready" if summary.get("transfers_executed", 0) > 0 else "Idle",
        "error": None,
        "summary": summary
    }
