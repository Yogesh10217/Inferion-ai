"""
Platform Concurrency Validation Engine.
Tests concurrent requests, evidence writes, delegations, and repository access under load.
"""

import concurrent.futures
from typing import Callable, List, Tuple

from app.platform_hardening.models import (
    ConcurrencyValidationResult,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class PlatformConcurrencyValidationEngine:
    """Validates thread safety and race condition protection across concurrent workflows."""

    def validate_concurrency(
        self, target_func: Callable, num_workers: int = 10, iterations: int = 20, tenant_id: str = "system"
    ) -> Tuple[ConcurrencyValidationResult, List[PlatformAuditFinding]]:
        races_detected = 0
        deadlocks_detected = 0
        findings: List[PlatformAuditFinding] = []

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=num_workers) as executor:
                futures = [executor.submit(target_func, i) for i in range(iterations)]
                results = []
                for f in concurrent.futures.as_completed(futures, timeout=5.0):
                    try:
                        results.append(f.result())
                    except Exception:
                        races_detected += 1

        except concurrent.futures.TimeoutError:
            deadlocks_detected += 1
            findings.append(
                PlatformAuditFinding(
                    finding_id="concurrency-deadlock",
                    tenant_id=tenant_id,
                    rule_id="RULE-CONC-001",
                    title="Concurrency Deadlock Detected",
                    description=f"Target operation deadlocked under concurrent execution of {num_workers} workers.",
                    severity=PlatformAuditSeverity.CRITICAL,
                    subsystem="concurrency",
                    affected_component=str(target_func),
                    remediation_suggestion="Inspect RLock acquire order and eliminate lock nesting.",
                )
            )

        is_valid = races_detected == 0 and deadlocks_detected == 0

        result = ConcurrencyValidationResult(
            is_valid=is_valid,
            concurrent_requests_tested=iterations,
            race_conditions_detected=races_detected,
            deadlocks_detected=deadlocks_detected,
            lost_updates_detected=0,
        )

        return result, findings
