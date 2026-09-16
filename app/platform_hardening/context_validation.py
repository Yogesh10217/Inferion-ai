"""
Cross-Phase Context Validation Engine.
Validates end-to-end propagation and preservation of tenant_id, trace_id, correlation_id, causation_id, and evidence.
"""

from typing import Dict, List, Tuple

from app.platform_hardening.models import (
    ContextPropagationResult,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class CrossPhaseContextValidationEngine:
    """Validates context propagation completeness across intelligence phase boundaries."""

    REQUIRED_CONTEXT_FIELDS = [
        "tenant_id",
        "trace_id",
        "correlation_id",
        "causation_id",
        "confidence",
        "evidence_reference",
    ]

    def validate_context_flow(
        self, context_payload: Dict, tenant_id: str = "system"
    ) -> Tuple[ContextPropagationResult, List[PlatformAuditFinding]]:
        missing_fields: List[str] = []
        findings: List[PlatformAuditFinding] = []

        tenant_preserved = bool(context_payload.get("tenant_id"))
        trace_preserved = bool(context_payload.get("trace_id"))
        correlation_preserved = bool(context_payload.get("correlation_id"))
        causation_preserved = bool(context_payload.get("causation_id"))
        confidence_preserved = "confidence" in context_payload
        evidence_preserved = bool(context_payload.get("evidence_reference"))

        for field in self.REQUIRED_CONTEXT_FIELDS:
            if field not in context_payload or context_payload[field] is None:
                missing_fields.append(field)
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"ctx-missing-{field}",
                        tenant_id=tenant_id,
                        rule_id="RULE-CTX-001",
                        title=f"Context Field Missing: '{field}'",
                        description=f"Context field '{field}' was dropped during cross-phase context propagation.",
                        severity=PlatformAuditSeverity.HIGH if field in ["tenant_id", "trace_id"] else PlatformAuditSeverity.MEDIUM,
                        subsystem="context_flow",
                        affected_component="CrossPhaseContext",
                        remediation_suggestion=f"Ensure '{field}' is passed into context builder across all phases.",
                    )
                )

        is_valid = len(missing_fields) == 0

        result = ContextPropagationResult(
            is_valid=is_valid,
            tenant_id_preserved=tenant_preserved,
            trace_id_preserved=trace_preserved,
            correlation_id_preserved=correlation_preserved,
            causation_id_preserved=causation_preserved,
            confidence_preserved=confidence_preserved,
            evidence_reference_preserved=evidence_preserved,
            missing_fields=missing_fields,
        )

        return result, findings
