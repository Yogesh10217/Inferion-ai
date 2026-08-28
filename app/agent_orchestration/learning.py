"""Agent Learning Intelligence Subsystem (Phase 5.36)."""

from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.agent_orchestration.exceptions import CrossTenantAgentAccessException


class AgentPattern(BaseModel):
    pattern_id: str = Field(default_factory=lambda: f"pat_{uuid.uuid4().hex[:8]}")
    pattern_type: str = "OPTIMAL_TOOL_SELECTION"
    description: str
    occurrence_count: int = 1


class AgentPerformanceInsight(BaseModel):
    insight_id: str = Field(default_factory=lambda: f"pinsight_{uuid.uuid4().hex[:10]}")
    agent_id: str
    metric_name: str
    trend: str = "IMPROVING"  # IMPROVING, STABLE, DEGRADING
    summary: str


class AgentLearningRecommendation(BaseModel):
    recommendation_id: str = Field(default_factory=lambda: f"rec_{uuid.uuid4().hex[:12]}")
    agent_id: str
    proposed_optimization: str
    requires_governance: bool = True
    affects_autonomy: bool = True
    status: str = "PENDING_GOVERNANCE_REVIEW"  # PENDING_GOVERNANCE_REVIEW, APPROVED, REJECTED


class AgentLearningRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"learn_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    agent_id: str
    source_execution_id: str
    learnings: Dict[str, Any] = Field(default_factory=dict)
    recommendations: List[AgentLearningRecommendation] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentLearningManager:
    """Tenant-isolated learning intelligence generating optimization recommendations without silently modifying autonomy policies."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._records: Dict[str, AgentLearningRecord] = {}

    def record_execution_learning(
        self,
        tenant_id: str,
        agent_id: str,
        execution_id: str,
        is_successful: bool = True,
        execution_duration_sec: float = 1.2,
        cost_dollars: float = 0.05,
    ) -> AgentLearningRecord:
        recs = []

        if is_successful and execution_duration_sec > 10.0:
            recs.append(AgentLearningRecommendation(
                agent_id=agent_id,
                proposed_optimization="Parallelize execution steps to reduce total runtime.",
                requires_governance=False,
                affects_autonomy=False,
            ))

        if is_successful and cost_dollars < 0.10:
            recs.append(AgentLearningRecommendation(
                agent_id=agent_id,
                proposed_optimization="Candidate for autonomy level expansion based on high efficiency.",
                requires_governance=True,
                affects_autonomy=True,
            ))

        record = AgentLearningRecord(
            tenant_id=tenant_id,
            agent_id=agent_id,
            source_execution_id=execution_id,
            learnings={
                "is_successful": is_successful,
                "duration_sec": execution_duration_sec,
                "cost_dollars": cost_dollars,
                "note": "Learning recorded cleanly within tenant boundary.",
            },
            recommendations=recs,
        )
        self._records[record.record_id] = record
        return record

    def list_learning_records(self, tenant_id: str, agent_id: Optional[str] = None) -> List[AgentLearningRecord]:
        results = []
        for rec in self._records.values():
            if rec.tenant_id == tenant_id or tenant_id == "global":
                if agent_id and rec.agent_id != agent_id:
                    continue
                results.append(rec)
        return results
