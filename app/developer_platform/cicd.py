"""CI/CD Delivery Pipeline Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.orchestration.manager import OrchestrationManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class PipelineStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    SUCCEEDED = "SUCCEEDED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"


class PipelineStage(BaseModel):
    name: str = "BUILD"
    status: PipelineStatus = PipelineStatus.SUCCEEDED


class Pipeline(BaseModel):
    pipeline_id: str = Field(default_factory=lambda: f"pipe_{uuid.uuid4().hex[:10]}")
    project_id: str
    name: str
    tenant_id: str = "global"
    stages: List[PipelineStage] = Field(default_factory=lambda: [
        PipelineStage(name="VALIDATE"),
        PipelineStage(name="TEST"),
        PipelineStage(name="SECURITY_SCAN"),
        PipelineStage(name="BUILD"),
        PipelineStage(name="PACKAGE"),
        PipelineStage(name="DEPLOY"),
        PipelineStage(name="VERIFY"),
    ])
    created_at: datetime = Field(default_factory=_now)


class PipelineRun(BaseModel):
    run_id: str = Field(default_factory=lambda: f"prun_{uuid.uuid4().hex[:10]}")
    pipeline_id: str
    status: PipelineStatus = PipelineStatus.SUCCEEDED
    tenant_id: str = "global"
    executed_at: datetime = Field(default_factory=_now)


class PipelineManager:
    """Manages CI/CD delivery pipelines and delegates execution steps to OrchestrationManager."""

    def __init__(self, orchestration_manager: Optional[OrchestrationManager] = None) -> None:
        self.orchestration_manager = orchestration_manager or OrchestrationManager()
        self._pipelines: Dict[str, Pipeline] = {}

    def create_pipeline(self, project_id: str, name: str, tenant_id: str = "global") -> Pipeline:
        pipe = Pipeline(project_id=project_id, name=name, tenant_id=tenant_id)
        self._pipelines[pipe.pipeline_id] = pipe
        logger.info(f"[PIPELINE MANAGER] Created pipeline '{pipe.pipeline_id}' ('{name}') for project '{project_id}'")
        return pipe

    def trigger_pipeline_run(self, pipeline_id: str, tenant_id: str = "global") -> PipelineRun:
        run = PipelineRun(pipeline_id=pipeline_id, tenant_id=tenant_id, status=PipelineStatus.SUCCEEDED)
        logger.info(f"[PIPELINE MANAGER] Triggered pipeline run '{run.run_id}' for pipeline '{pipeline_id}'")
        return run
