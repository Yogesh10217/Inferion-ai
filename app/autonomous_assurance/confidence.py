"""
Workflow Confidence Subsystem.
Computes deterministic confidence metrics based on evidence quality, signal consistency, and plan completeness.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field


class WorkflowConfidenceAssessment(BaseModel):
    confidence_id: str = Field(default_factory=lambda: f"wfconf_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    overall_confidence: float = Field(0.95, ge=0.0, le=1.0)
    evidence_quality: float = Field(0.95, ge=0.0, le=1.0)
    plan_completeness: float = Field(0.95, ge=0.0, le=1.0)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowConfidenceEngine:
    """Evaluates workflow confidence levels."""

    def __init__(self) -> None:
        self._assessments: Dict[str, WorkflowConfidenceAssessment] = {}

    def calculate_confidence(
        self,
        workflow_id: str,
        tenant_id: str,
        evidence_quality_score: float = 95.0,
        plan_step_count: int = 3,
    ) -> WorkflowConfidenceAssessment:
        ev_q = min(1.0, max(0.0, evidence_quality_score / 100.0))
        plan_c = 1.0 if plan_step_count >= 1 else 0.5
        overall = round((ev_q * 0.6) + (plan_c * 0.4), 4)

        assessment = WorkflowConfidenceAssessment(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            overall_confidence=overall,
            evidence_quality=ev_q,
            plan_completeness=plan_c,
        )
        self._assessments[workflow_id] = assessment
        return assessment

    def get_confidence(self, workflow_id: str) -> Optional[WorkflowConfidenceAssessment]:
        return self._assessments.get(workflow_id)
