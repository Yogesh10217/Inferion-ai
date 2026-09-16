"""
Platform Production Readiness Engine.
Calculates empirical, weighted platform readiness scores backed by actual audit evidence.
"""

from typing import Dict, List

from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class PlatformProductionReadinessEngine:
    """Calculates weighted readiness scores (0-100) based strictly on empirical audit findings."""

    def calculate_readiness_report(self, findings: List[PlatformAuditFinding], tenant_id: str = "system") -> Dict[str, float]:
        # Deduct penalties per component category from baseline score of 100.0
        scores = {
            "integration": 100.0,
            "architecture": 100.0,
            "reliability": 100.0,
            "security": 100.0,
            "governance": 100.0,
            "traceability": 100.0,
            "evidence": 100.0,
            "testing": 100.0,
            "maintainability": 100.0,
        }

        for f in findings:
            penalty = 5.0
            if f.severity == PlatformAuditSeverity.CRITICAL:
                penalty = 25.0
            elif f.severity == PlatformAuditSeverity.HIGH:
                penalty = 15.0
            elif f.severity == PlatformAuditSeverity.MEDIUM:
                penalty = 8.0

            sub = f.subsystem.lower()
            rule = f.rule_id.lower()

            if "int" in rule or "prov" in rule or "eng" in rule:
                scores["integration"] = max(0.0, scores["integration"] - penalty)
            elif "dep" in rule or "dup" in rule or "mgr" in rule:
                scores["architecture"] = max(0.0, scores["architecture"] - penalty)
            elif "ctx" in rule or "trace" in rule:
                scores["traceability"] = max(0.0, scores["traceability"] - penalty)
            elif "ev" in rule:
                scores["evidence"] = max(0.0, scores["evidence"] - penalty)
            elif "gov" in rule or "del" in rule:
                scores["governance"] = max(0.0, scores["governance"] - penalty)
            elif "repo" in rule or "tenant" in f.title.lower():
                scores["security"] = max(0.0, scores["security"] - penalty)
            elif "stub" in rule or "dead" in rule:
                scores["maintainability"] = max(0.0, scores["maintainability"] - penalty)
            else:
                scores["reliability"] = max(0.0, scores["reliability"] - penalty)

        # Weighted calculation
        overall_score = (
            scores["integration"] * 0.15
            + scores["architecture"] * 0.15
            + scores["reliability"] * 0.10
            + scores["security"] * 0.15
            + scores["governance"] * 0.15
            + scores["traceability"] * 0.10
            + scores["evidence"] * 0.10
            + scores["testing"] * 0.05
            + scores["maintainability"] * 0.05
        )

        scores["overall"] = round(overall_score, 1)
        return scores
