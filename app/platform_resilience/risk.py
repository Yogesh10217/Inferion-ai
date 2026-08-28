"""Resilience Risk Composition Subsystem (Phase 5.37)."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.platform_contracts.tenant import TenantAccessGuard
from app.governance_platform.risk import RiskManager


class ResilienceRiskDimension(str, Enum):
    DEPENDENCY = "DEPENDENCY"
    CAPACITY = "CAPACITY"
    FAILOVER = "FAILOVER"
    RECOVERY = "RECOVERY"
    DATA_INTEGRITY = "DATA_INTEGRITY"


class ResilienceRiskProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"resriskprof_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    overall_risk_score: float = 0.2
    risk_level: str = "LOW"  # LOW, MEDIUM, HIGH, CRITICAL
    dimension_scores: Dict[ResilienceRiskDimension, float] = Field(default_factory=dict)


class ResilienceRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"resriskeval_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    resource_id: str
    risk_score: float = 0.2
    risk_level: str = "LOW"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ResilienceRiskManager:
    """Resilience Risk Composition Manager reusing GovernancePlatform's RiskManager."""

    def __init__(
        self,
        governance_risk_manager: Optional[RiskManager] = None,
        tenant_guard: Optional[TenantAccessGuard] = None,
    ) -> None:
        self.governance_risk_manager = governance_risk_manager or RiskManager()
        self.tenant_guard = tenant_guard or TenantAccessGuard()

    def assess_resilience_risk(
        self,
        tenant_id: str,
        resource_id: str,
        is_failover_pending: bool = False,
        capacity_utilization_pct: float = 50.0,
    ) -> ResilienceRiskAssessment:
        base_score = capacity_utilization_pct / 100.0 * 0.5
        if is_failover_pending:
            base_score += 0.45

        risk_score = min(1.0, base_score)
        
        level = "LOW"
        if risk_score >= 0.8:
            level = "CRITICAL"
        elif risk_score >= 0.6:
            level = "HIGH"
        elif risk_score >= 0.4:
            level = "MEDIUM"

        return ResilienceRiskAssessment(
            tenant_id=tenant_id,
            resource_id=resource_id,
            risk_score=risk_score,
            risk_level=level,
        )
