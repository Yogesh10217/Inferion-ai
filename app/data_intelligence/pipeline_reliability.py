"""Pipeline reliability intelligence (Phase 5.43)."""

import uuid
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field

from app.data_intelligence.exceptions import CrossTenantDataIntelligenceException
from app.data_intelligence.pipelines import DataPipelineManager, PipelineHealth


class PipelineFailure(BaseModel):
    failure_id: str
    pipeline_id: str
    tenant_id: str
    error_type: str
    error_message: str
    occurred_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PipelineReliabilityScore(BaseModel):
    pipeline_id: str
    tenant_id: str
    reliability_score: float  # 0.0 - 1.0
    mttr_minutes: float
    mtbf_hours: float
    summary: str


class PipelineReliabilityAssessment(BaseModel):
    assessment_id: str
    tenant_id: str
    overall_reliability_score: float
    pipeline_scores: List[PipelineReliabilityScore] = Field(default_factory=list)
    failures_count: int
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PipelineReliabilityManager:
    """Evaluates pipeline reliability in integration with platform resilience and event intelligence."""

    def __init__(self, pipeline_manager: Optional[DataPipelineManager] = None) -> None:
        self.pipeline_manager = pipeline_manager or DataPipelineManager()
        self._failures: Dict[str, List[PipelineFailure]] = {}

    def record_failure(
        self,
        pipeline_id: str,
        tenant_id: str,
        error_type: str,
        error_message: str,
    ) -> PipelineFailure:
        pipe = self.pipeline_manager.get_pipeline(pipeline_id, tenant_id)
        fid = f"pfail-{uuid.uuid4().hex[:8]}"

        fail = PipelineFailure(
            failure_id=fid,
            pipeline_id=pipeline_id,
            tenant_id=tenant_id,
            error_type=error_type,
            error_message=error_message,
        )
        if pipeline_id not in self._failures:
            self._failures[pipeline_id] = []
        self._failures[pipeline_id].append(fail)

        pipe.health = PipelineHealth.UNHEALTHY
        return fail

    def evaluate_reliability(self, tenant_id: str, pipeline_id: Optional[str] = None) -> PipelineReliabilityAssessment:
        pipes = [p for p in self.pipeline_manager._pipelines.values() if p.tenant_id == tenant_id]
        if pipeline_id:
            pipes = [p for p in pipes if p.pipeline_id == pipeline_id]

        scores = []
        total_fails = 0

        for p in pipes:
            fails = self._failures.get(p.pipeline_id, [])
            total_fails += len(fails)

            score_val = max(0.0, 1.0 - (len(fails) * 0.2))
            prs = PipelineReliabilityScore(
                pipeline_id=p.pipeline_id,
                tenant_id=tenant_id,
                reliability_score=round(score_val, 4),
                mttr_minutes=float(len(fails) * 15),
                mtbf_hours=float(max(1.0, 100.0 / max(1, len(fails)))),
                summary=f"Pipeline {p.pipeline_id} score={score_val:.2f} ({len(fails)} failures)",
            )
            scores.append(prs)

        avg_score = sum([s.reliability_score for s in scores]) / max(1, len(scores))
        aid = f"pra-{uuid.uuid4().hex[:8]}"

        return PipelineReliabilityAssessment(
            assessment_id=aid,
            tenant_id=tenant_id,
            overall_reliability_score=round(avg_score, 4),
            pipeline_scores=scores,
            failures_count=total_fails,
        )
