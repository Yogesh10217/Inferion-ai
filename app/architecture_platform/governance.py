"""Architecture Governance & Policy Evaluation Subsystem."""

from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.governance_platform.policy_evaluation import UnifiedPolicyEvaluator
from app.governance_platform.risk import RiskManager
from app.approvals.approval_engine import ApprovalEngine
from app.architecture_platform.impact import ImpactAnalysis, ImpactSeverity


class ArchitecturePolicyDecisionType(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    REQUIRE_APPROVAL = "REQUIRE_APPROVAL"
    RESTRICT = "RESTRICT"
    BLOCK = "BLOCK"


class ArchitectureRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"risk_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    target_node_id: str
    risk_score: float  # 0.0 - 100.0
    risk_level: str  # LOW, MEDIUM, HIGH, CRITICAL
    factors: List[str] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitecturePolicyDecision(BaseModel):
    decision_id: str = Field(default_factory=lambda: f"poldec_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    decision: ArchitecturePolicyDecisionType
    requires_approval: bool = False
    approval_request_id: Optional[str] = None
    reason: str
    risk_assessment: ArchitectureRiskAssessment
    decided_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ArchitectureGovernanceEngine:
    """Evaluates architectural policies and enforces human approval for high-risk changes."""

    def __init__(
        self,
        policy_evaluator: Optional[UnifiedPolicyEvaluator] = None,
        risk_manager: Optional[RiskManager] = None,
        approval_engine: Optional[ApprovalEngine] = None,
    ) -> None:
        self.policy_evaluator = policy_evaluator or UnifiedPolicyEvaluator()
        self.risk_manager = risk_manager or RiskManager()
        self.approval_engine = approval_engine or ApprovalEngine()

    def evaluate_change_governance(
        self,
        tenant_id: str,
        target_node_id: str,
        impact_analysis: ImpactAnalysis,
        requested_by: str = "system",
    ) -> ArchitecturePolicyDecision:
        severity = impact_analysis.blast_radius.estimated_severity
        affected_count = impact_analysis.blast_radius.total_affected_count
        action_type = impact_analysis.action_type

        factors = [f"Blast radius severity: {severity.value}", f"Affected nodes: {affected_count}", f"Action type: {action_type}"]
        
        if severity in (ImpactSeverity.HIGH, ImpactSeverity.CRITICAL) or action_type in ("REMOVE", "MIGRATE", "REPLACE") or affected_count >= 5:
            risk_score = 85.0
            risk_level = "HIGH" if severity == ImpactSeverity.HIGH or action_type == "REMOVE" else "CRITICAL"
        elif severity == ImpactSeverity.MEDIUM:
            risk_score = 50.0
            risk_level = "MEDIUM"
        else:
            risk_score = 20.0
            risk_level = "LOW"


        risk_assessment = ArchitectureRiskAssessment(
            tenant_id=tenant_id,
            target_node_id=target_node_id,
            risk_score=risk_score,
            risk_level=risk_level,
            factors=factors,
        )

        requires_approval = False
        approval_request_id = None
        decision_type = ArchitecturePolicyDecisionType.ALLOW
        reason = "Architecture change evaluated and approved."

        if risk_level in ("HIGH", "CRITICAL"):
            requires_approval = True
            decision_type = ArchitecturePolicyDecisionType.REQUIRE_APPROVAL
            reason = f"High-risk architecture change (Risk: {risk_level}) requires explicit approval."

            # Request approval from ApprovalEngine
            app_req = self.approval_engine.request_approval(
                execution_id=target_node_id,
                action_type=f"ARCHITECTURE_CHANGE_{impact_analysis.action_type}",
                requester=requested_by,
                tenant_id=tenant_id,
                payload={"target_node_id": target_node_id, "risk_level": risk_level},
            )
            approval_request_id = app_req.request_id

        elif risk_level == "MEDIUM":
            decision_type = ArchitecturePolicyDecisionType.WARN
            reason = "Medium-risk change approved with warning."

        return ArchitecturePolicyDecision(
            tenant_id=tenant_id,
            decision=decision_type,
            requires_approval=requires_approval,
            approval_request_id=approval_request_id,
            reason=reason,
            risk_assessment=risk_assessment,
        )
