"""Enterprise Background Job Models & Lifecycle States."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class JobStatus(str, Enum):
    PENDING = "PENDING"
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    RETRYING = "RETRYING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    DEAD_LETTER = "DEAD_LETTER"


class JobPriority(int, Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


class JobMetadata(BaseModel):
    """Context metadata attached to a job."""

    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    trace_id: Optional[str] = None
    execution_id: Optional[str] = None
    idempotency_key: Optional[str] = None
    custom_headers: Dict[str, Any] = Field(default_factory=dict)


class JobResult(BaseModel):
    """Result output of executed job."""

    job_id: str
    status: JobStatus
    output: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    duration_ms: float = 0.0
    attempts: int = 1


class Job(BaseModel):
    """Distributed job entity."""

    job_id: str = Field(default_factory=lambda: f"job_{uuid.uuid4().hex[:12]}")
    name: str
    handler_name: str
    payload: Dict[str, Any] = Field(default_factory=dict)
    priority: JobPriority = JobPriority.NORMAL
    status: JobStatus = JobStatus.PENDING
    metadata: JobMetadata = Field(default_factory=JobMetadata)
    max_attempts: int = 3
    attempts_made: int = 0
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    scheduled_at: Optional[datetime] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    lease_owner: Optional[str] = None
    lease_expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
