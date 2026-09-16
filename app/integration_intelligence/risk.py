"""Integration Risk Intelligence (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException


class IntegrationRiskDimension(str, Enum):
    SYSTEM_CRITICALITY = "SYSTEM_CRITICALITY"
    ACTION_SENSITIVITY = "ACTION_SENSITIVITY"
    DATA_SENSITIVITY = "DATA_SENSITIVITY"
    BLAST_RADIUS = "BLAST_RADIUS"
    EXECUTION_TRUST = "EXECUTION_TRUST"
    DEPENDENCY_RISK = "DEPENDENCY_RISK"
    FINANCIAL_IMPACT = "FINANCIAL_IMPACT"


class IntegrationRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"risk_prof_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_id: str
    overall_risk_score: float = 0.0
    risk_level: str = "LOW"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class IntegrationRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"risk_eval_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    workflow_id: str
    composite_risk_score: float = 0.0
    is_high_risk: bool = False
    profile: IntegrationRiskProfile


class IntegrationRiskManager:
    """Composes with RiskManager to compute multi-dimensional integration risk."""

    def __init__(self) -> None:
        self._assessments: Dict[str, IntegrationRiskAssessment] = {}

    def calculate_risk(
        self,
        tenant_id: str,
        workflow_id: str,
        system_criticality_score: float = 20.0,
        action_sensitivity_score: float = 20.0,
        data_sensitivity_score: float = 20.0,
        blast_radius_score: float = 20.0,
        is_destructive: bool = False,
    ) -> IntegrationRiskAssessment:
        base_score = (system_criticality_score + action_sensitivity_score + data_sensitivity_score + blast_radius_score) / 4.0
        if is_destructive:
            base_score = max(base_score, 85.0)

        composite = round(base_score, 2)
        if composite >= 80.0:
            level = "CRITICAL"
        elif composite >= 60.0:
            level = "HIGH"
        elif composite >= 40.0:
            level = "MEDIUM"
        else:
            level = "LOW"

        prof = IntegrationRiskProfile(
            tenant_id=tenant_id,
            target_id=workflow_id,
            overall_risk_score=composite,
            risk_level=level,
        )

        asm = IntegrationRiskAssessment(
            tenant_id=tenant_id,
            workflow_id=workflow_id,
            composite_risk_score=composite,
            is_high_risk=composite >= 75.0,
            profile=prof,
        )
        self._assessments[asm.assessment_id] = asm
        return asm

    def get_assessment(self, tenant_id: str, assessment_id: str) -> IntegrationRiskAssessment:
        asm = self._assessments.get(assessment_id)
        if not asm or asm.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return asm
