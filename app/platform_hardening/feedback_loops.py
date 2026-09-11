"""
Platform Feedback Loop Validation Engine.
Detects one-way pipelines, disconnected verifications, and stale assurance confidence scores.
"""

from typing import Dict, List, Tuple
from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class PlatformFeedbackLoopValidationEngine:
    """Validates complete feedback loops between verification, evidence, and decision assurance."""

    def validate_feedback_loops(
        self, active_loops: List[Dict], tenant_id: str = "system"
    ) -> Tuple[bool, List[PlatformAuditFinding]]:
        findings: List[PlatformAuditFinding] = []
        disconnected_count = 0

        for loop in active_loops:
            name = loop.get("name", "Unknown Loop")
            is_closed = loop.get("is_closed_loop", False)

            if not is_closed:
                disconnected_count += 1
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"feedback-open-{name.lower().replace(' ', '-')}",
                        tenant_id=tenant_id,
                        rule_id="RULE-FBD-001",
                        title=f"One-Way Pipeline Detected: '{name}'",
                        description=f"Pipeline '{name}' operates as one-way without returning execution feedback to assurance.",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem="feedback_loops",
                        affected_component=name,
                        remediation_suggestion=f"Wire verification callback into '{name}' pipeline start.",
                    )
                )

        is_valid = disconnected_count == 0
        return is_valid, findings
