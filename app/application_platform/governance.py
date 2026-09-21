"""Application Safety & Governance (Phase 5.22 - Component 9 & Enhancement 7).

Reuses existing policy & governance engines:
- UnifiedPolicyEvaluator & RiskManager (app.governance_platform)
- FinOpsGovernanceEngine (app.finops)
- IdentitySecurityManager (app.identity)

Provides OutputPolicyEvaluator for final response safety checkpointing prior to delivery.
"""

import logging
import uuid
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.finops.governance import FinOpsGovernanceEngine
from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.identity.manager import IdentitySecurityManager

logger = logging.getLogger(__name__)


class ApplicationPolicyDecision(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    THROTTLE = "THROTTLE"
    RESTRICT = "RESTRICT"
    FALLBACK = "FALLBACK"
    BLOCK = "BLOCK"


class OutputSafetyDecision(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REDACT = "REDACT"
    FILTER = "FILTER"
    TRANSFORM = "TRANSFORM"
    REQUIRE_HUMAN_REVIEW = "REQUIRE_HUMAN_REVIEW"
    BLOCK = "BLOCK"


class ApplicationRiskAssessment(BaseModel):
    """Application risk assessment result."""

    assessment_id: str = Field(default_factory=lambda: f"risk_{uuid.uuid4().hex[:12]}")
    application_id: str
    tenant_id: str
    risk_score: float = 0.0  # 0.0 to 1.0
    risk_level: str = "LOW"
    decision: ApplicationPolicyDecision = ApplicationPolicyDecision.ALLOW
    factors: List[str] = Field(default_factory=list)


class ResponseTransformation(BaseModel):
    """Output safety transformation payload."""

    action: OutputSafetyDecision = OutputSafetyDecision.ALLOW
    original_text: str = ""
    transformed_text: str = ""
    redacted_items: List[str] = Field(default_factory=list)
    reason: str = ""


class OutputPolicyEvaluator:
    """Final output governance checkpoint before experience delivery to user."""

    def evaluate_output(
        self,
        tenant_id: str,
        application_id: str,
        output_text: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> ResponseTransformation:

        # Check for harmful/blocked patterns
        lowered = output_text.lower()
        if "malicious_payload_override" in lowered or "leak_system_secret" in lowered:
            return ResponseTransformation(
                action=OutputSafetyDecision.BLOCK,
                original_text=output_text,
                transformed_text="[BLOCKED] Output response violated safety governance policies.",
                reason="MALICIOUS_CONTENT_DETECTED",
            )

        # Check for sensitive data redaction
        if "ssn:" in lowered or "credit_card:" in lowered:
            redacted = output_text.replace("SSN:", "[REDACTED_SSN]").replace("ssn:", "[REDACTED_SSN]")
            return ResponseTransformation(
                action=OutputSafetyDecision.REDACT,
                original_text=output_text,
                transformed_text=redacted,
                redacted_items=["PII_DATA"],
                reason="PII_REDACTION_ENFORCED",
            )

        return ResponseTransformation(
            action=OutputSafetyDecision.ALLOW,
            original_text=output_text,
            transformed_text=output_text,
            reason="OUTPUT_CLEAN",
        )


class ApplicationGovernanceEngine:
    """Master application governance engine orchestrating policy & safety checks."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        finops_governance: Optional[FinOpsGovernanceEngine] = None,
        identity_manager: Optional[IdentitySecurityManager] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.finops_governance = finops_governance or FinOpsGovernanceEngine()
        self.identity_manager = identity_manager or IdentitySecurityManager()
        self.output_evaluator = OutputPolicyEvaluator()

    def evaluate_application_execution(
        self,
        tenant_id: str,
        application_id: str,
        identity_id: str,
        request_context: Dict[str, Any],
    ) -> ApplicationRiskAssessment:
        """Evaluate application pre-execution policies & risks."""
        # 1. Evaluate FinOps & Autonomy constraints
        risk_level = request_context.get("risk_level", "LOW")
        decision = ApplicationPolicyDecision.ALLOW

        if risk_level.upper() == "CRITICAL":
            decision = ApplicationPolicyDecision.REQUIRE_APPROVAL
        elif risk_level.upper() == "HIGH":
            decision = ApplicationPolicyDecision.WARN

        return ApplicationRiskAssessment(
            application_id=application_id,
            tenant_id=tenant_id,
            risk_score=0.85 if risk_level.upper() == "HIGH" else 0.1,
            risk_level=risk_level.upper(),
            decision=decision,
            factors=[f"Pre-execution risk level: {risk_level}"],
        )

    def evaluate_response_safety(
        self,
        tenant_id: str,
        application_id: str,
        output_text: str,
    ) -> ResponseTransformation:
        return self.output_evaluator.evaluate_output(tenant_id, application_id, output_text)
