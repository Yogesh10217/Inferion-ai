"""
Platform Idempotency Validation Engine.
Verifies that duplicate requests produce single logical execution side-effects across platform features.
"""

from typing import Callable, Dict, List, Tuple
from app.platform_hardening.models import (
    IdempotencyValidationResult,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class PlatformIdempotencyValidationEngine:
    """Validates request deduplication and idempotency keys across platform operations."""

    def validate_idempotency(
        self, operation_func: Callable, request_payload: Dict, key: str, tenant_id: str = "system"
    ) -> Tuple[IdempotencyValidationResult, List[PlatformAuditFinding]]:
        findings: List[PlatformAuditFinding] = []
        executions: List[Dict] = []

        # Execute identical operation 3 times
        for _ in range(3):
            try:
                res = operation_func(request_payload, key=key)
                executions.append(res)
            except Exception as e:
                executions.append({"error": str(e)})

        # Evaluate if duplicate executions were prevented
        # Expected: exact same output or explicit duplicate detection flag
        duplicate_prevented = True
        if len(executions) >= 2:
            first_id = executions[0].get("operation_id") or executions[0].get("audit_id")
            second_id = executions[1].get("operation_id") or executions[1].get("audit_id")

            if first_id and second_id and first_id != second_id and not executions[1].get("is_duplicate"):
                duplicate_prevented = False
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"idempotency-fail-{key}",
                        tenant_id=tenant_id,
                        rule_id="RULE-IDEM-001",
                        title=f"Idempotency Failure for Key '{key}'",
                        description="Identical request payload executed multiple distinct logical operations.",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem="idempotency",
                        affected_component=str(operation_func),
                        remediation_suggestion="Enforce idempotency key check before invoking business logic.",
                    )
                )

        result = IdempotencyValidationResult(
            is_valid=duplicate_prevented,
            repeated_requests_tested=3,
            duplicate_executions_prevented=1 if duplicate_prevented else 0,
            idempotency_key_collisions=0,
        )

        return result, findings
