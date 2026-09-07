"""Operational trust intelligence adapting results to platform TrustAssessment primitive."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

from app.governance_platform.trust import TrustAssessment, TrustFactor, TrustDimension


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
            TrustFactor(name="Availability", weight=0.4, score=availability),
            TrustFactor(name="Reliability", weight=0.4, score=reliability),
            TrustFactor(name="Governance", weight=0.2, score=1.0 if governance_passed else 0.0),
        ]
        overall = sum(f.weight * f.score for f in factors)

        assessment = TrustAssessment(
            tenant_id=tenant_id,
            entity_id=service_id,
            entity_type="SERVICE",
            trust_score=round(overall, 4),
            factors=factors,
        )

        if tenant_id not in self._assessments:
            self._assessments[tenant_id] = {}
        self._assessments[tenant_id][service_id] = assessment
        return assessment

    def get_trust_assessment(self, tenant_id: str, service_id: str) -> Optional[TrustAssessment]:
        return self._assessments.get(tenant_id, {}).get(service_id)
