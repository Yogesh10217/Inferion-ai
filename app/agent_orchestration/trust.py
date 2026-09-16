"""Agent Trust Evaluation Subsystem (Phase 5.36)."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from app.agent_orchestration.exceptions import CrossTenantAgentAccessException
from app.platform_contracts.tenant import TenantAccessGuard
from app.platform_contracts.trust import TrustAssessment, TrustBand, TrustConfidence, TrustDimension


class AgentTrustDimension(str, Enum):
    RELIABILITY = "RELIABILITY"
    POLICY_COMPLIANCE = "POLICY_COMPLIANCE"
    VERIFICATION_SUCCESS = "VERIFICATION_SUCCESS"
    HUMAN_OVERRIDE_RATE = "HUMAN_OVERRIDE_RATE"
    FAILURE_RATE = "FAILURE_RATE"
    EVIDENCE_QUALITY = "EVIDENCE_QUALITY"


class AgentTrustFactor(BaseModel):
    dimension: AgentTrustDimension
    score: float = 90.0  # 0 to 100
    weight: float = 1.0


class AgentTrustScore(BaseModel):
    agent_id: str
    tenant_id: str
    overall_score: float = 92.5
    band: TrustBand = TrustBand.HIGH_TRUST
    factors: List[AgentTrustFactor] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AgentTrustEngine:
    """Evaluates agent trust metrics and converts evaluations into platform-compliant TrustAssessments."""

    def __init__(self, tenant_guard: Optional[TenantAccessGuard] = None) -> None:
        self.tenant_guard = tenant_guard or TenantAccessGuard()
        self._scores: Dict[str, AgentTrustScore] = {}

    def calculate_agent_trust(
        self,
        tenant_id: str,
        agent_id: str,
        success_count: int = 10,
        failure_count: int = 0,
        policy_violations: int = 0,
        human_overrides: int = 0,
    ) -> TrustAssessment:
        total = max(1, success_count + failure_count)
        success_rate = (success_count / total) * 100.0

        rel_score = max(0.0, success_rate - (failure_count * 10.0))
        pol_score = max(0.0, 100.0 - (policy_violations * 20.0))
        hum_score = max(0.0, 100.0 - (human_overrides * 15.0))

        factors = [
            AgentTrustFactor(dimension=AgentTrustDimension.RELIABILITY, score=rel_score, weight=1.5),
            AgentTrustFactor(dimension=AgentTrustDimension.POLICY_COMPLIANCE, score=pol_score, weight=2.0),
            AgentTrustFactor(dimension=AgentTrustDimension.VERIFICATION_SUCCESS, score=rel_score, weight=1.0),
            AgentTrustFactor(dimension=AgentTrustDimension.HUMAN_OVERRIDE_RATE, score=hum_score, weight=1.0),
        ]

        total_weight = sum(f.weight for f in factors)
        weighted_sum = sum(f.score * f.weight for f in factors)
        overall = weighted_sum / total_weight if total_weight > 0 else 90.0

        if overall >= 90.0:
            band = TrustBand.HIGH_TRUST
        elif overall >= 70.0:
            band = TrustBand.TRUSTED
        elif overall >= 50.0:
            band = TrustBand.RESTRICTED
        else:
            band = TrustBand.UNTRUSTED

        self._scores[agent_id] = AgentTrustScore(
            agent_id=agent_id,
            tenant_id=tenant_id,
            overall_score=overall,
            band=band,
            factors=factors,
        )

        dims = [TrustDimension(dimension_name=f.dimension.value, score=f.score, weight=f.weight) for f in factors]

        return TrustAssessment(
            subject_type="ENTERPRISE_AGENT",
            subject_id=agent_id,
            tenant_id=tenant_id,
            score=overall,
            band=band,
            confidence=TrustConfidence.HIGH,
            dimensions=dims,
            evidence_references=[f"ev_trust_{agent_id}"],
        )

    def get_trust_assessment(self, agent_id: str, tenant_id: str) -> TrustAssessment:
        score = self._scores.get(agent_id)
        if score:
            try:
                self.tenant_guard.enforce_isolation(tenant_id, score.tenant_id)
            except Exception:
                raise CrossTenantAgentAccessException(tenant_id, score.tenant_id)

        return self.calculate_agent_trust(tenant_id=tenant_id, agent_id=agent_id)
