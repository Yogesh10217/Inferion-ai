"""
Platform Remediation Planner.
Generates RemediationRecommendation items with mandatory auto_execute = False enforcement.
"""

from typing import List

from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
    RemediationRecommendation,
)


class PlatformRemediationPlanner:
    """Generates remediation plans for audit findings enforcing auto_execute=False safety invariant."""

    def generate_remediations(
        self, findings: List[PlatformAuditFinding], tenant_id: str = "system"
    ) -> List[RemediationRecommendation]:
        remediations: List[RemediationRecommendation] = []

        for f in findings:
            priority = "P3"
            if f.severity == PlatformAuditSeverity.CRITICAL:
                priority = "P0"
            elif f.severity == PlatformAuditSeverity.HIGH:
                priority = "P1"
            elif f.severity == PlatformAuditSeverity.MEDIUM:
                priority = "P2"

            rem = RemediationRecommendation(
                remediation_id=f"rem-{f.finding_id}",
                tenant_id=tenant_id,
                finding_id=f.finding_id,
                severity=f.severity,
                subsystem=f.subsystem,
                affected_component=f.affected_component,
                root_cause_hypothesis=f.root_cause_hypothesis or "Architectural flaw or integration gap.",
                recommendation=f.remediation_suggestion or f"Resolve finding '{f.title}'.",
                risk=f.severity.value,
                priority=priority,
                requires_approval=True,
                auto_execute=False,  # Mandatory Invariant 6: ALWAYS False
            )
            remediations.append(rem)

        return remediations
