"""
Autonomous Assurance Subsystem.
Computes overall continuous assurance metrics and rating bands for workflows.
"""

import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field


class AutonomousAssuranceScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"assur_{uuid.uuid4().hex[:12]}")
    workflow_id: str
    tenant_id: str
    overall_assurance_score: float = Field(92.5, ge=0.0, le=100.0)
    assurance_rating: str = "HIGH_ASSURANCE"
    compliance_status: str = "COMPLIANT"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AutonomousAssuranceEngine:
    """Evaluates continuous autonomous assurance scores."""

    def __init__(self) -> None:
        self._scores: Dict[str, AutonomousAssuranceScore] = {}

    def calculate_assurance(
        self,
        workflow_id: str,
        tenant_id: str,
        confidence_score: float = 0.95,
        trust_score: float = 90.0,
        verification_passed: bool = True,
    ) -> AutonomousAssuranceScore:
        base = trust_score * 0.5 + (confidence_score * 100.0) * 0.3 + (100.0 if verification_passed else 40.0) * 0.2
        overall = round(max(0.0, min(100.0, base)), 2)
        rating = "HIGH_ASSURANCE" if overall >= 80.0 else ("MEDIUM_ASSURANCE" if overall >= 60.0 else "LOW_ASSURANCE")

        score = AutonomousAssuranceScore(
            workflow_id=workflow_id,
            tenant_id=tenant_id,
            overall_assurance_score=overall,
            assurance_rating=rating,
        )
        self._scores[workflow_id] = score
        return score

    def get_assurance(self, workflow_id: str) -> Optional[AutonomousAssuranceScore]:
        return self._scores.get(workflow_id)
