"""Control Assurance Risk Composition Subsystem (Phase 5.38)."""

import uuid
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.governance_platform.risk import RiskManager
from app.platform_contracts.tenant import TenantAccessGuard


class ControlRiskDimension(str, Enum):
    CONTROL_FAILURE = "CONTROL_FAILURE"
    COMPLIANCE_EXPOSURE = "COMPLIANCE_EXPOSURE"
    DATA_LEAKAGE = "DATA_LEAKAGE"
    AI_BIAS = "AI_BIAS"
    RELIABILITY_DEGRADATION = "RELIABILITY_DEGRADATION"


class ControlRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"crisk_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    risk_score: float = 45.0
    risk_level: str = "MODERATE"
    dimension: ControlRiskDimension = ControlRiskDimension.CONTROL_FAILURE


class ControlRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"rprof_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    overall_risk_score: float = 45.0
    risk_level: str = "MODERATE"
    assessments: List[ControlRiskAssessment] = Field(default_factory=list)


class ControlRiskManager:
    """Composes control assurance risk profiles with enterprise RiskManager."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self.enterprise_risk_manager = RiskManager()
        self._profiles: Dict[str, ControlRiskProfile] = {}

    def assess_control_risk(self, tenant_id: str, control_id: str, is_failed: bool = False) -> ControlRiskProfile:
        score = 85.0 if is_failed else 25.0
        level = "HIGH" if is_failed else "LOW"

        ass = ControlRiskAssessment(
            tenant_id=tenant_id,
            control_id=control_id,
            risk_score=score,
            risk_level=level,
        )

        prof = ControlRiskProfile(
            tenant_id=tenant_id,
            control_id=control_id,
            overall_risk_score=score,
            risk_level=level,
            assessments=[ass],
        )
        self._profiles[control_id] = prof
        return prof
