"""
Platform Release Gate Engine.
Enforces strict release readiness gates blocking release on P0 findings, tenant leaks, or approval bypasses.
"""

from typing import List

from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
    ReleaseGateResult,
    ReleaseReadinessDecision,
)


class PlatformReleaseGateEngine:
    """Evaluates audit findings and security invariants to emit binding ReleaseReadinessDecisions."""

    def evaluate_release_gate(
        self,
        findings: List[PlatformAuditFinding],
        cross_tenant_leak: bool = False,
        direct_infra_mutation: bool = False,
        approval_bypass: bool = False,
        broken_evidence_chain: bool = False,
    ) -> ReleaseGateResult:

        p0_count = sum(1 for f in findings if f.severity == PlatformAuditSeverity.CRITICAL)
        p1_count = sum(1 for f in findings if f.severity == PlatformAuditSeverity.HIGH)

        # Rule 1: Mandatory Blocks
        if (
            p0_count > 0
            or cross_tenant_leak
            or direct_infra_mutation
            or approval_bypass
            or broken_evidence_chain
        ):
            reasons = []
            if p0_count > 0:
                reasons.append(f"{p0_count} P0 critical finding(s) exist")
            if cross_tenant_leak:
                reasons.append("Cross-tenant leakage detected")
            if direct_infra_mutation:
                reasons.append("Direct infrastructure mutation attempted")
            if approval_bypass:
                reasons.append("Human approval gate bypassed")
            if broken_evidence_chain:
                reasons.append("Evidence hash chain corrupted or tampered")

            return ReleaseGateResult(
                decision=ReleaseReadinessDecision.BLOCKED,
                blocking_p0_count=p0_count,
                cross_tenant_leak_detected=cross_tenant_leak,
                direct_infra_mutation_detected=direct_infra_mutation,
                approval_bypass_detected=approval_bypass,
                broken_evidence_chain_detected=broken_evidence_chain,
                reason="Release BLOCKED: " + "; ".join(reasons),
            )

        # Rule 2: Conditional Approval if P1 findings exist
        if p1_count > 0:
            return ReleaseGateResult(
                decision=ReleaseReadinessDecision.CONDITIONALLY_APPROVED,
                blocking_p0_count=0,
                cross_tenant_leak_detected=False,
                direct_infra_mutation_detected=False,
                approval_bypass_detected=False,
                broken_evidence_chain_detected=False,
                reason=f"Release CONDITIONALLY APPROVED: {p1_count} P1 finding(s) pending remediation.",
            )

        # Rule 3: Full Approval
        return ReleaseGateResult(
            decision=ReleaseReadinessDecision.APPROVED,
            blocking_p0_count=0,
            cross_tenant_leak_detected=False,
            direct_infra_mutation_detected=False,
            approval_bypass_detected=False,
            broken_evidence_chain_detected=False,
            reason="Release APPROVED: All platform integration, governance, and security gates passed.",
        )
