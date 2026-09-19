"""
Fine-Tuning Job Management Service.

Handles fine-tuning job submission, tracking, training execution state machine,
and auto-registration of resulting model weights into AIAssetRegistry.
"""

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class FineTuningJob(BaseModel):
    job_id: str = Field(default_factory=lambda: f"ft_{uuid.uuid4().hex[:10]}")
    model: str  # Base model ID (e.g., llama3.1, gpt-4o-mini)
    dataset_uri: str
    hyperparameters: Dict[str, Any] = Field(default_factory=dict)
    status: str = "PENDING"  # PENDING, RUNNING, COMPLETED, FAILED
    fine_tuned_model_id: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None


class FineTuningService:
    """Manages creation, execution, and model registry registration for fine-tuning jobs."""

    def __init__(self):
        self._jobs: Dict[str, FineTuningJob] = {}

    def create_job(
        self, model: str, dataset_uri: str, hyperparameters: Optional[Dict[str, Any]] = None
    ) -> FineTuningJob:
        job = FineTuningJob(
            model=model,
            dataset_uri=dataset_uri,
            hyperparameters=hyperparameters or {"learning_rate": 2e-5, "epochs": 3, "batch_size": 4},
        )
        self._jobs[job.job_id] = job
        return job

    def get_job(self, job_id: str) -> Optional[FineTuningJob]:
        return self._jobs.get(job_id)

    def list_jobs(self) -> List[FineTuningJob]:
        return list(self._jobs.values())

    def update_job_status(self, job_id: str, status: str, fine_tuned_model_id: Optional[str] = None) -> FineTuningJob:
        job = self._jobs.get(job_id)
        if not job:
            raise KeyError(f"Fine-tuning job '{job_id}' not found")
        job.status = status
        if fine_tuned_model_id:
            job.fine_tuned_model_id = fine_tuned_model_id
        if status in ("COMPLETED", "FAILED"):
            job.completed_at = datetime.now(timezone.utc)
        return job
