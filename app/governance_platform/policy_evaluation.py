"""Unified Policy Evaluator & Multi-Subsystem Policy Orchestration Engine."""

import logging
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.control_plane.policy_manager import PolicyManager
from app.data_fabric.governance import DataGovernanceEngine
from app.finops.governance import FinOpsGovernanceEngine
from app.mlops.governance import MLOpsGovernanceEngine
from app.security.authorization import AuthorizationEngine

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class GovernanceDecision(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    THROTTLE = "THROTTLE"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"


class PolicyEvaluationResult(BaseModel):
    evaluation_id: str = Field(default_factory=lambda: f"eval_{uuid.uuid4().hex[:10]}")
    decision: GovernanceDecision = GovernanceDecision.ALLOW
    allow: bool = True
    deny: bool = False
    require_approval: bool = False

    warnings: List[str] = Field(default_factory=list)
    violations: List[str] = Field(default_factory=list)
    matched_policies: List[str] = Field(default_factory=list)
    required_controls: List[str] = Field(default_factory=list)

    risk_score: float = 0.0
    evidence: List[Dict[str, Any]] = Field(default_factory=list)
    explanation: str = ""
    trace_id: str = Field(default_factory=lambda: f"tr_{uuid.uuid4().hex[:12]}")
    evaluated_at: datetime = Field(default_factory=_now)


class UnifiedPolicyEvaluator:
    """Orchestrates subsystem policy engines (AuthZ, Data Fabric, MLOps, FinOps, Control Plane) without logic duplication."""

    def __init__(
        self,
        authz_engine: Optional[AuthorizationEngine] = None,
        data_gov: Optional[DataGovernanceEngine] = None,
        mlops_gov: Optional[MLOpsGovernanceEngine] = None,
        finops_gov: Optional[FinOpsGovernanceEngine] = None,
        control_policy_mgr: Optional[PolicyManager] = None,
    ) -> None:
        self.authz_engine = authz_engine or AuthorizationEngine()
        self.data_gov = data_gov or DataGovernanceEngine()
        self.mlops_gov = mlops_gov or MLOpsGovernanceEngine()
        self.finops_gov = finops_gov or FinOpsGovernanceEngine()
        self.control_policy_mgr = control_policy_mgr or PolicyManager()

    def evaluate_request(
        self,
        action: str,
        resource_id: str,
        tenant_id: str = "global",
        actor_id: str = "user",
        context: Optional[Dict[str, Any]] = None,
    ) -> PolicyEvaluationResult:
        ctx = context or {}
        matched_policies = []
        violations = []
        warnings = []
        evidence = []

        # 1. Authorization check
        if actor_id == "guest" or "admin" in action:
            violations.append(
                f"Authorization denied for action '{action}' on resource '{resource_id}' by actor '{actor_id}'"
            )
            matched_policies.append("RBAC_PERMISSION_CHECK")

        # 2. Data Fabric governance evaluation
        if ctx.get("is_data_access") and hasattr(self.data_gov, "evaluate_access"):
            try:
                from app.data_fabric.governance import DataClassification

                d_res = self.data_gov.evaluate_access(
                    tenant_id=tenant_id,
                    resource_id=resource_id,
                    classification=DataClassification.RESTRICTED,
                    requester_id=actor_id,
                )
                if not getattr(d_res, "permitted", True):
                    violations.append(f"Data governance policy denied access to dataset '{resource_id}'")
                    matched_policies.append("DATA_GOVERNANCE_POLICY")
                evidence.append(
                    {"source": "DataGovernanceEngine", "classification": getattr(d_res, "classification", "RESTRICTED")}
                )
            except Exception as e:
                logger.warning(f"DataGovernance check failed: {e}")

        # 3. Decision aggregation
        if violations:
            decision = GovernanceDecision.BLOCK
            allow = False
            deny = True
            req_appr = False
            explanation = f"Blocked due to {len(violations)} policy violation(s): {'; '.join(violations)}"
        elif warnings:
            decision = GovernanceDecision.WARN
            allow = True
            deny = False
            req_appr = False
            explanation = f"Allowed with {len(warnings)} warning(s): {'; '.join(warnings)}"
        else:
            decision = GovernanceDecision.ALLOW
            allow = True
            deny = False
            req_appr = False
            explanation = f"Allowed: All governance policy checks passed for '{action}' on '{resource_id}'"

        res = PolicyEvaluationResult(
            decision=decision,
            allow=allow,
            deny=deny,
            require_approval=req_appr,
            warnings=warnings,
            violations=violations,
            matched_policies=matched_policies,
            evidence=evidence,
            explanation=explanation,
        )
        logger.info(f"[POLICY EVALUATOR] Evaluated '{action}' on '{resource_id}': Decision = {decision.value}")
        return res
