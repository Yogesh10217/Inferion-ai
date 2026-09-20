"""FastAPI Router for Distributed Job Management (/v1/jobs)."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.jobs.job import Job, JobMetadata, JobPriority
from app.jobs.job_queue import JobQueue

router = APIRouter(prefix="/jobs", tags=["jobs"])

_global_job_queue = JobQueue()


def get_job_queue() -> JobQueue:
    return _global_job_queue


class CreateJobSchema(BaseModel):
    name: str
    handler_name: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: int = 5
    tenant_id: str = "global"
    idempotency_key: Optional[str] = None


@router.post("", status_code=status.HTTP_201_CREATED)
async def enqueue_job(data: CreateJobSchema, queue: JobQueue = Depends(get_job_queue)):
    """Enqueue a new background job."""
    job = Job(
        name=data.name,
        handler_name=data.handler_name,
        payload=data.payload,
        priority=JobPriority(data.priority) if data.priority in [p.value for p in JobPriority] else JobPriority.NORMAL,
        metadata=JobMetadata(tenant_id=data.tenant_id, idempotency_key=data.idempotency_key),
    )
    enqueued = queue.enqueue(job)
    return {"status": "enqueued", "job": enqueued.model_dump()}


@router.get("")
async def list_jobs(status_filter: Optional[str] = None, queue: JobQueue = Depends(get_job_queue)):
    """List jobs filtered by status."""
    jobs = list(queue._jobs.values())
    if status_filter:
        jobs = [j for j in jobs if j.status.value == status_filter.upper()]
    return {"jobs": [j.model_dump() for j in jobs]}


@router.get("/{id}")
async def get_job(id: str, queue: JobQueue = Depends(get_job_queue)):
    """Get job status and output by ID."""
    job = queue.get_status(id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{id}' not found")
    return {"job": job.model_dump()}


@router.post("/{id}/cancel")
async def cancel_job(id: str, queue: JobQueue = Depends(get_job_queue)):
    """Cancel a queued job."""
    try:
        job = queue.cancel(id)
        return {"status": "cancelled", "job": job.model_dump()}
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{id}' not found")


@router.post("/{id}/retry")
async def retry_job(id: str, queue: JobQueue = Depends(get_job_queue)):
    """Retry a failed or dead-letter job."""
    try:
        job = queue.retry(id)
        return {"status": "requeued", "job": job.model_dump()}
    except KeyError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{id}' not found")
