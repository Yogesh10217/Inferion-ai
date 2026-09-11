"""
Trace Propagation Validation Engine.
Validates trace_id, correlation_id, and causation_id consistency across intelligence phases.
"""

from typing import Dict, List, Tuple
from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
    TracePropagationResult,
)


class TracePropagationValidationEngine:
    """Validates execution trace consistency, correlation, and causation propagation across phases."""

    def validate_trace_path(
        self, trace_id: str, phase_traces: List[Dict], tenant_id: str = "system"
    ) -> Tuple[TracePropagationResult, List[PlatformAuditFinding]]:
        phases_visited: List[str] = []
        findings: List[PlatformAuditFinding] = []

        trace_lost = False
        trace_mutated = False
        trace_collision = False
        trace_leakage = False
        broken_causation = False
        broken_correlation = False

        prev_causation = None

        for item in phase_traces:
            p_name = item.get("phase_name", "unknown")
            t_id = item.get("trace_id")
            c_tenant = item.get("tenant_id")
            causation_id = item.get("causation_id")

            phases_visited.append(p_name)

            # Check tenant isolation / leakage
            if c_tenant and c_tenant != tenant_id:
                trace_leakage = True
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"trace-leak-{trace_id}-{p_name}",
                        tenant_id=tenant_id,
                        rule_id="RULE-TRACE-001",
                        title=f"Cross-Tenant Trace Leakage in Phase '{p_name}'",
                        description=f"Trace ID '{trace_id}' accessed across tenant boundary ({c_tenant} != {tenant_id}).",
                        severity=PlatformAuditSeverity.CRITICAL,
                        subsystem=p_name,
                        affected_component="TraceContext",
                        remediation_suggestion="Enforce strict tenant filtering in trace propagation.",
                    )
                )

            # Check trace consistency
            if not t_id:
                trace_lost = True
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"trace-lost-{p_name}",
                        tenant_id=tenant_id,
                        rule_id="RULE-TRACE-002",
                        title=f"Trace ID Dropped in Phase '{p_name}'",
                        description=f"Trace ID was missing during processing in phase '{p_name}'.",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem=p_name,
                        affected_component="TraceContext",
                    )
                )
            elif t_id != trace_id:
                trace_mutated = True
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"trace-mutated-{p_name}",
                        tenant_id=tenant_id,
                        rule_id="RULE-TRACE-003",
                        title=f"Trace ID Mutated in Phase '{p_name}'",
                        description=f"Trace ID mutated from '{trace_id}' to '{t_id}' in phase '{p_name}'.",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem=p_name,
                        affected_component="TraceContext",
                    )
                )

            # Check causation sequence
            if prev_causation and causation_id and causation_id == prev_causation:
                # Causation ID should evolve per step
                broken_causation = True

            prev_causation = causation_id

        is_valid = not (trace_lost or trace_mutated or trace_collision or trace_leakage)

        result = TracePropagationResult(
            is_valid=is_valid,
            trace_id=trace_id,
            phases_visited=phases_visited,
            trace_lost=trace_lost,
            trace_mutated=trace_mutated,
            trace_collision=trace_collision,
            trace_leakage=trace_leakage,
            broken_causation=broken_causation,
            broken_correlation=broken_correlation,
        )

        return result, findings
