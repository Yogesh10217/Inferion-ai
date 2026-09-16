"""
Cross-Phase Verification Validation Engine.
Validates closed-loop feedback from execution verification back into continuous assurance.
"""

from typing import Dict, List, Tuple

from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
    VerificationValidationResult,
)


class CrossPhaseVerificationValidationEngine:
    """Validates verification result feedback to assurance confidence models."""

    def validate_verification_loop(
        self, loop_payload: Dict, tenant_id: str = "system"
    ) -> Tuple[VerificationValidationResult, List[PlatformAuditFinding]]:
        findings: List[PlatformAuditFinding] = []

        verification_performed = bool(loop_payload.get("verification_id"))
        feedback_returned = bool(loop_payload.get("assurance_updated"))
        evidence_sealed = bool(loop_payload.get("evidence_id"))

        if verification_performed and not feedback_returned:
            findings.append(
                PlatformAuditFinding(
                    finding_id="ver-disconnected-feedback",
                    tenant_id=tenant_id,
                    rule_id="RULE-VER-001",
                    title="Verification Feedback Disconnected",
                    description="Execution verification was performed but result was not fed back into Continuous Assurance.",
                    severity=PlatformAuditSeverity.HIGH,
                    subsystem="verification",
                    affected_component="VerificationEngine",
                    root_cause_hypothesis="Verification engine did not call Continuous Assurance update API.",
                    remediation_suggestion="Invoke ContinuousAssuranceManager.update_confidence() upon verification completion.",
                )
            )

        if verification_performed and not evidence_sealed:
            findings.append(
                PlatformAuditFinding(
                    finding_id="ver-missing-evidence",
                    tenant_id=tenant_id,
                    rule_id="RULE-VER-002",
                    title="Verification Evidence Unsealed",
                    description="Verification completed without generating SHA-256 evidence record.",
                    severity=PlatformAuditSeverity.HIGH,
                    subsystem="verification",
                    affected_component="VerificationEngine",
                    remediation_suggestion="Seal verification outcome into EvidenceLedger.",
                )
            )

        is_valid = verification_performed and feedback_returned and evidence_sealed

        result = VerificationValidationResult(
            is_valid=is_valid,
            closed_loop_verified=is_valid,
            feedback_returned_to_assurance=feedback_returned,
        )

        return result, findings
