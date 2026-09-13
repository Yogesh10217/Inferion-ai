from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from app.deployment.models import PlatformReadinessClassification, ProductionReleaseDecision
from app.deployment.production_readiness import ProductionReadinessEvaluator, ProductionReadinessResult
from app.deployment.secrets import SecretsSanitizer


@dataclass
class ReleaseGovernanceDecisionResult:
    decision: ProductionReleaseDecision
    status_classification: PlatformReadinessClassification
    blocking_reasons: List[str]
    warnings: List[str]
    approval_granted: bool
    governance_message: str
    evaluated_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sanitized_dict(self) -> Dict[str, Any]:
        return SecretsSanitizer.sanitize_structure({
            "decision": self.decision.value,
            "status_classification": self.status_classification.value,
            "blocking_reasons": self.blocking_reasons,
            "warnings": self.warnings,
            "approval_granted": self.approval_granted,
            "governance_message": self.governance_message,
            "evaluated_at": self.evaluated_at,
        })


class ProductionReleaseDecisionEngine:
    """Canonical Release Go / No-Go Decision Engine determining deterministic release decisions."""

    def __init__(self, readiness_evaluator: Optional[ProductionReadinessEvaluator] = None) -> None:
        self.readiness_evaluator = readiness_evaluator or ProductionReadinessEvaluator()

    def evaluate_release_decision(
        self, external_evidence: Optional[Dict[str, Any]] = None
    ) -> ReleaseGovernanceDecisionResult:
        readiness_res = self.readiness_evaluator.evaluate_production_readiness(external_evidence)

        blocking = list(readiness_res.blocking_reasons)
        warnings = list(readiness_res.warnings)

        if len(blocking) > 0:
            decision = ProductionReleaseDecision.NO_GO
            classification = PlatformReadinessClassification.RUNTIME_BLOCKED
            approval_granted = False
            msg = "Release BLOCKED due to technical or security policy violations"
        elif readiness_res.readiness_status == "MANUAL_REVIEW_REQUIRED":
            decision = ProductionReleaseDecision.MANUAL_REVIEW_REQUIRED
            classification = PlatformReadinessClassification.PARTIALLY_VALIDATED
            approval_granted = False
            msg = "Release requires explicit human sign-off before entering production procedure"
        else:
            decision = ProductionReleaseDecision.GO
            classification = PlatformReadinessClassification.PRODUCTION_RELEASE_APPROVED
            approval_granted = True
            msg = "GO FOR CONTROLLED PRODUCTION RELEASE: Release candidate approved to enter production deployment procedure"

        return ReleaseGovernanceDecisionResult(
            decision=decision,
            status_classification=classification,
            blocking_reasons=blocking,
            warnings=warnings,
            approval_granted=approval_granted,
            governance_message=msg,
        )
