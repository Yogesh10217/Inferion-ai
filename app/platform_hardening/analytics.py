"""
Platform Hardening Analytics.
Aggregates audit findings, broken providers, disconnected engines, stubs, dead code, and certification status.
"""

from typing import Dict, List
from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class PlatformHardeningAnalytics:
    """Aggregates platform audit metrics across runs."""

    def compute_analytics(self, findings: List[PlatformAuditFinding]) -> Dict[str, int]:
        total_findings = len(findings)
        critical_findings = sum(1 for f in findings if f.severity == PlatformAuditSeverity.CRITICAL)
        high_findings = sum(1 for f in findings if f.severity == PlatformAuditSeverity.HIGH)
        medium_findings = sum(1 for f in findings if f.severity == PlatformAuditSeverity.MEDIUM)
        low_findings = sum(1 for f in findings if f.severity == PlatformAuditSeverity.LOW)

        stub_findings = sum(1 for f in findings if "stub" in f.finding_id)
        dead_code_findings = sum(1 for f in findings if "dead" in f.finding_id)
        duplicate_findings = sum(1 for f in findings if "dup" in f.finding_id)
        dependency_violations = sum(1 for f in findings if "dep" in f.finding_id)

        return {
            "total_findings": total_findings,
            "critical_findings": critical_findings,
            "high_findings": high_findings,
            "medium_findings": medium_findings,
            "low_findings": low_findings,
            "stub_findings": stub_findings,
            "dead_code_findings": dead_code_findings,
            "duplicate_findings": duplicate_findings,
            "dependency_violations": dependency_violations,
        }
