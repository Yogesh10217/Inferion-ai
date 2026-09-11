"""
Cross-Phase Governance Validation Engine.
Validates governance gates (ALLOW, DENY, REQUIRE_APPROVAL, ADVISORY_ONLY) and prevents approval bypass.
"""

from typing import Dict, List, Tuple
from app.platform_hardening.models import (
    GovernanceValidationResult,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class CrossPhaseGovernanceValidationEngine:
    """Validates governance policy enforcement and human approval gate integrity across high-risk flows."""

    def validate_governance_flow(
        self, flow_context: Dict, tenant_id: str = "system"
    ) -> Tuple[GovernanceValidationResult, List[PlatformAuditFinding]]:
        findings: List[PlatformAuditFinding] = []

        risk_level = flow_context.get("risk_level", "LOW")
        governance_decision = flow_context.get("governance_decision", "ALLOW")
        has_human_approval = flow_context.get("has_human_approval", False)
        delegation_created = flow_context.get("delegation_created", False)

        approval_bypasses = 0

        # Rule: If risk is HIGH or CRITICAL, or governance_decision is REQUIRE_APPROVAL, human approval is mandatory before delegation
        if (risk_level in ["HIGH", "CRITICAL"] or governance_decision == "REQUIRE_APPROVAL"):
            if delegation_created and not has_human_approval:
                approval_bypasses += 1
                findings.append(
                    PlatformAuditFinding(
                        finding_id="gov-approval-bypass",
                        tenant_id=tenant_id,
                        rule_id="RULE-GOV-001",
                        title="Human Governance Approval Bypass Detected",
                        description=f"High-risk action (risk: {risk_level}, decision: {governance_decision}) delegated without human approval.",
                        severity=PlatformAuditSeverity.CRITICAL,
                        subsystem="governance",
                        affected_component="GovernanceGate",
                        root_cause_hypothesis="Delegation engine failed to verify human approval token before creating delegation request.",
                        remediation_suggestion="Block delegation request creation when governance requires approval and has_human_approval is False.",
                    )
                )

        if governance_decision == "DENY" and delegation_created:
            approval_bypasses += 1
            findings.append(
                PlatformAuditFinding(
                    finding_id="gov-deny-bypass",
                    tenant_id=tenant_id,
                    rule_id="RULE-GOV-002",
                    title="Governance DENY Policy Bypass Detected",
                    description="Delegation request created despite governance decision being DENY.",
                    severity=PlatformAuditSeverity.CRITICAL,
                    subsystem="governance",
                    affected_component="GovernanceGate",
                    remediation_suggestion="Immediately reject delegation request generation when governance decision is DENY.",
                )
            )

        is_valid = approval_bypasses == 0

        result = GovernanceValidationResult(
            is_valid=is_valid,
            gates_tested=["ALLOW", "DENY", "REQUIRE_APPROVAL", "ADVISORY_ONLY"],
            approval_bypasses_detected=approval_bypasses,
            high_risk_gates_enforced=is_valid,
        )

        return result, findings
