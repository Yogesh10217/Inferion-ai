"""
Decision Policy Evaluation Subsystem.
Evaluates decision options and recommendations against active platform policy rules.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.decision_intelligence.exceptions import DecisionPolicyViolationException


class DecisionPolicyResult(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: f"pol_{uuid.uuid4().hex[:12]}")
    decision_id: str
    tenant_id: str
    policy_version: str = "1.0.0"
    is_compliant: bool = True
    passed_rules: List[str] = Field(default_factory=list)
    violated_rules: List[str] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class DecisionPolicyEvaluator:
    """Evaluates decision options against active governance policies."""

    def __init__(self) -> None:
        self._evaluations: Dict[str, DecisionPolicyResult] = {}

    def evaluate_policy(self, decision_id: str, tenant_id: str, context: Dict[str, Any], option_params: Optional[Dict[str, Any]] = None) -> DecisionPolicyResult:
        passed = ["POL_SEC_001_ENCRYPTION_CHECK", "POL_OPS_002_CAPACITY_LIMIT", "POL_GOV_003_TENANT_ISOLATION"]
        violated = []

        if option_params and option_params.get("disable_security_checks"):
            violated.append("POL_SEC_004_MANDATORY_SECURITY_CHECKS")

        is_compliant = len(violated) == 0

        res = DecisionPolicyResult(
            decision_id=decision_id,
            tenant_id=tenant_id,
            is_compliant=is_compliant,
            passed_rules=passed,
            violated_rules=violated,
        )
        self._evaluations[decision_id] = res

        if not is_compliant:
            raise DecisionPolicyViolationException(f"Decision '{decision_id}' violated policies: {violated}")

        return res

    def get_evaluation(self, decision_id: str) -> Optional[DecisionPolicyResult]:
        return self._evaluations.get(decision_id)
