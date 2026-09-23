"""Operational trust intelligence adapting results to platform TrustAssessment primitive."""

from typing import Dict, Optional

from app.governance_platform.trust import TrustAssessment, TrustDimension, TrustFactor


class OperationsTrustEngine:
    """Evaluates operational trust and adapts output to standard platform TrustAssessment."""

    def __init__(self) -> None:
        self._assessments: Dict[str, Dict[str, TrustAssessment]] = {}  # tenant_id -> {service_id: TrustAssessment}

    def evaluate_trust(
        self,
        tenant_id: str,
        service_id: str,
        availability: float = 0.999,
        reliability: float = 0.95,
        governance_passed: bool = True,
    ) -> TrustAssessment:
        factors = [
            TrustFactor(
                dimension=TrustDimension.RELIABILITY, weight=0.4, score=availability * 100.0, description="Availability"
            ),
            TrustFactor(
                dimension=TrustDimension.RELIABILITY, weight=0.4, score=reliability * 100.0, description="Reliability"
            ),
            TrustFactor(
                dimension=TrustDimension.COMPLIANCE,
                weight=0.2,
                score=100.0 if governance_passed else 0.0,
                description="Governance",
            ),
        ]
        total_weight = sum(f.weight for f in factors)
        weighted_score = sum(f.score * f.weight for f in factors) / total_weight if total_weight > 0 else 100.0

        assessment = TrustAssessment(
            tenant_id=tenant_id,
            target_resource_id=service_id,
            overall_trust_score=round(weighted_score, 2),
            factors=factors,
        )

        if tenant_id not in self._assessments:
            self._assessments[tenant_id] = {}
        self._assessments[tenant_id][service_id] = assessment
        return assessment

    def get_trust_assessment(self, tenant_id: str, service_id: str) -> Optional[TrustAssessment]:
        return self._assessments.get(tenant_id, {}).get(service_id)
