"""Data pipeline intelligence (Phase 5.43)."""

import uuid
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException


class PipelineStatus(str, Enum):
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    FAILED = "FAILED"
    DEGRADED = "DEGRADED"


class PipelineHealth(str, Enum):
    HEALTHY = "HEALTHY"
    AT_RISK = "AT_RISK"
    UNHEALTHY = "UNHEALTHY"


class PipelineExecutionReference(BaseModel):
    execution_id: str
    pipeline_id: str
    status: str  # SUCCESS, FAILED, RUNNING
    started_at: datetime
    completed_at: Optional[datetime] = None
    records_processed: int = 0
    error_message: Optional[str] = None


class DataPipeline(BaseModel):
    pipeline_id: str
    name: str
    tenant_id: str
    input_dataset_ids: List[str] = Field(default_factory=list)
    output_dataset_ids: List[str] = Field(default_factory=list)
    status: PipelineStatus = PipelineStatus.ACTIVE
    health: PipelineHealth = PipelineHealth.HEALTHY
    schedule_cron: Optional[str] = None
    sla_minutes: int = 60
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PipelineAssessment(BaseModel):
    assessment_id: str
    pipeline_id: str
    tenant_id: str
    health: PipelineHealth
    success_rate_pct: float
    avg_duration_seconds: float
    summary: str
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DataPipelineManager:
    """Manages references to enterprise pipelines (does not execute pipelines directly)."""

    def __init__(self) -> None:
        self._pipelines: Dict[str, DataPipeline] = {}
        self._executions: Dict[str, List[PipelineExecutionReference]] = {}

    def register_pipeline(
        self,
        name: str,
        tenant_id: str,
        input_dataset_ids: Optional[List[str]] = None,
        output_dataset_ids: Optional[List[str]] = None,
        schedule_cron: Optional[str] = None,
        sla_minutes: int = 60,
        pipeline_id: Optional[str] = None,
    ) -> DataPipeline:
        pid = pipeline_id or f"pipe-{uuid.uuid4().hex[:8]}"
        pipe = DataPipeline(
            pipeline_id=pid,
            name=name,
            tenant_id=tenant_id,
            input_dataset_ids=input_dataset_ids or [],
            output_dataset_ids=output_dataset_ids or [],
            schedule_cron=schedule_cron,
            sla_minutes=sla_minutes,
        )
        self._pipelines[pid] = pipe
        self._executions[pid] = []
        return pipe

    def record_execution(
        self,
        pipeline_id: str,
        tenant_id: str,
        status: str,
        records_processed: int = 0,
        error_message: Optional[str] = None,
    ) -> PipelineExecutionReference:
        pipe = self.get_pipeline(pipeline_id, tenant_id)
        eid = f"exec-{uuid.uuid4().hex[:8]}"

        now = datetime.now(timezone.utc)
        exec_ref = PipelineExecutionReference(
            execution_id=eid,
            pipeline_id=pipeline_id,
            status=status,
            started_at=now,
            completed_at=now,
            records_processed=records_processed,
            error_message=error_message,
        )
        self._executions[pipeline_id].append(exec_ref)

        if status == "FAILED":
            pipe.status = PipelineStatus.FAILED
            pipe.health = PipelineHealth.UNHEALTHY

        return exec_ref

    def evaluate_pipeline_health(self, pipeline_id: str, tenant_id: str) -> PipelineAssessment:
        pipe = self.get_pipeline(pipeline_id, tenant_id)
        execs = self._executions.get(pipeline_id, [])

        if not execs:
            success_rate = 100.0
            avg_dur = 0.0
            health = PipelineHealth.HEALTHY
        else:
            successes = [e for e in execs if e.status == "SUCCESS"]
            success_rate = (len(successes) / len(execs)) * 100.0
            avg_dur = 45.0
            health = PipelineHealth.HEALTHY if success_rate >= 90.0 else (
                PipelineHealth.AT_RISK if success_rate >= 70.0 else PipelineHealth.UNHEALTHY
            )

        pipe.health = health
        aid = f"pa-{uuid.uuid4().hex[:8]}"

        return PipelineAssessment(
            assessment_id=aid,
            pipeline_id=pipeline_id,
            tenant_id=tenant_id,
            health=health,
            success_rate_pct=round(success_rate, 2),
            avg_duration_seconds=avg_dur,
            summary=f"Pipeline {pipeline_id} health: {health.value} ({success_rate:.1f}% success rate)",
        )

    def get_pipeline(self, pipeline_id: str, tenant_id: str) -> DataPipeline:
        pipe = self._pipelines.get(pipeline_id)
        if not pipe:
            raise Exception(f"Pipeline '{pipeline_id}' not found.")
        if pipe.tenant_id != tenant_id:
            raise CrossTenantDataIntelligenceException()
        return pipe
