"""Platform Integration Governance Evaluation Engine (Phase 5.58)."""

import logging

from app.platform_integration.models import (
    GovernanceDecision,
    RiskLevel,
)

logger = logging.getLogger(__name__)


class PlatformIntegrationGovernanceEngine:
    """Evaluates risks and policies to enforce ALLOW, DENY, REQUIRE_APPROVAL, or ADVISORY_ONLY."""

    def evaluate_governance(
        self,
        tenant_id: str,
        action: str,
        risk_level: RiskLevel,
        confidence: float = 0.9,
    ) -> GovernanceDecision:
        # Deny critical risks if confidence is weak
        if risk_level == RiskLevel.CRITICAL and confidence < 0.6:
            logger.warning(f"Governance DENY: Action '{action}' has CRITICAL risk with low confidence ({confidence}).")
            return GovernanceDecision.DENY

        # High or Critical risks strictly require human approval
        if risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
            logger.info(f"Governance REQUIRE_APPROVAL: Action '{action}' risk={risk_level.value}")
            return GovernanceDecision.REQUIRE_APPROVAL

        # Medium risk with moderate confidence
        if risk_level == RiskLevel.MEDIUM:
            return GovernanceDecision.ADVISORY_ONLY

        # Low risk allows advisory recommendation
        return GovernanceDecision.ALLOW
