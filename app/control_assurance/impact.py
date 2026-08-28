"""Assurance Impact Analysis Subsystem (Phase 5.38)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.control_assurance.exceptions import CrossTenantControlAssuranceAccessException


class ControlImpactDimension(str, Enum):
    SECURITY = "SECURITY"
    COMPLIANCE = "COMPLIANCE"
    DATA = "DATA"
    RELIABILITY = "RELIABILITY"
    AVAILABILITY = "AVAILABILITY"
    FINANCIAL = "FINANCIAL"
    CUSTOMER = "CUSTOMER"
    AI_SAFETY = "AI_SAFETY"
    OPERATIONAL = "OPERATIONAL"


class ControlImpactSeverity(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ControlImpactAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"imp_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    control_id: str
    severity: ControlImpactSeverity = ControlImpactSeverity.HIGH
    affected_dimensions: List[ControlImpactDimension] = Field(default_factory=list)
    impact_score: float = 75.0
    summary: str = ""


class ControlImpactAnalyzer:
    """Analyzes multi-dimensional impact of control failures and policy gaps."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()

    def analyze_impact(
        self,
        tenant_id: str,
        control_id: str,
        affected_dimensions: Optional[List[ControlImpactDimension]] = None,
    ) -> ControlImpactAssessment:
        dims = affected_dimensions or [ControlImpactDimension.SECURITY, ControlImpactDimension.COMPLIANCE]
        score = 85.0 if ControlImpactDimension.SECURITY in dims else 60.0
        sev = ControlImpactSeverity.CRITICAL if score > 80 else ControlImpactSeverity.HIGH

        return ControlImpactAssessment(
            tenant_id=tenant_id,
            control_id=control_id,
            severity=sev,
            affected_dimensions=dims,
            impact_score=score,
            summary=f"Impact assessment for control '{control_id}' affecting {len(dims)} dimensions.",
        )
