"""
Cross-Phase Delegation Validation Engine.
Enforces Mandated Invariant 2 & 6: auto_execute MUST BE False on all delegation requests.
"""

from typing import Dict, List, Tuple
from app.platform_hardening.models import (
    DelegationValidationResult,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class CrossPhaseDelegationValidationEngine:
    """Validates DelegationRequest objects and ensures advisory safety (auto_execute = False)."""

    def validate_delegation(
        self, delegation_payload: Dict, tenant_id: str = "system"
    ) -> Tuple[DelegationValidationResult, List[PlatformAuditFinding]]:
        findings: List[PlatformAuditFinding] = []

        auto_execute = delegation_payload.get("auto_execute", False)
        del_tenant = delegation_payload.get("tenant_id")
        direct_exec = delegation_payload.get("direct_infrastructure_mutation", False)

        auto_execute_false_enforced = (auto_execute is False)
        direct_executions = 0
        cross_tenant_delegations = 0

        # Mandatory Invariant Check: auto_execute MUST BE False
        if auto_execute is not False:
            findings.append(
                PlatformAuditFinding(
                    finding_id="del-auto-execute-violation",
                    tenant_id=tenant_id,
                    rule_id="RULE-DEL-001",
                    title="Mandatory Invariant Violation: auto_execute is True",
                    description="DelegationRequest has auto_execute=True violating Advisory Safety Invariants 2 & 6.",
                    severity=PlatformAuditSeverity.CRITICAL,
                    subsystem="delegation",
                    affected_component="DelegationRequest",
                    root_cause_hypothesis="Delegation generator explicitly set auto_execute=True.",
                    remediation_suggestion="Force auto_execute=False on all DelegationRequest initializers.",
                )
            )

        if direct_exec:
            direct_executions += 1
            findings.append(
                PlatformAuditFinding(
                    finding_id="del-direct-exec-violation",
                    tenant_id=tenant_id,
                    rule_id="RULE-DEL-002",
                    title="Direct Infrastructure Mutation Attempted",
                    description="Delegation request attempted direct infrastructure mutation instead of advisory delegation.",
                    severity=PlatformAuditSeverity.CRITICAL,
                    subsystem="delegation",
                    affected_component="DelegationEngine",
                    remediation_suggestion="Remove direct execution logic; emit advisory DelegationRequest only.",
                )
            )

        if del_tenant and del_tenant != tenant_id:
            cross_tenant_delegations += 1
            findings.append(
                PlatformAuditFinding(
                    finding_id="del-cross-tenant-violation",
                    tenant_id=tenant_id,
                    rule_id="RULE-DEL-003",
                    title="Cross-Tenant Delegation Attempted",
                    description=f"Delegation request created for tenant '{del_tenant}' from context '{tenant_id}'.",
                    severity=PlatformAuditSeverity.CRITICAL,
                    subsystem="delegation",
                    affected_component="DelegationEngine",
                    remediation_suggestion="Restrict delegation creation to active request tenant.",
                )
            )

        is_valid = auto_execute_false_enforced and direct_executions == 0 and cross_tenant_delegations == 0

        result = DelegationValidationResult(
            is_valid=is_valid,
            auto_execute_false_enforced=auto_execute_false_enforced,
            direct_executions_detected=direct_executions,
            cross_tenant_delegations_detected=cross_tenant_delegations,
        )

        return result, findings
