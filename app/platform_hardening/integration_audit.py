"""
Cross-Phase Integration Audit Engine.
Executes end-to-end integration audits across all 8 upper intelligence platforms.
"""

from typing import List, Tuple

from app.platform_hardening.models import (
    IntegrationHealth,
    IntegrationHealthStatus,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)
from app.platform_hardening.subsystem_registry import SubsystemRegistry


class CrossPhaseIntegrationAuditEngine:
    """Audits cross-phase connectivity and integration health across all 8 intelligence platforms."""

    def __init__(self, registry: SubsystemRegistry):
        self.registry = registry

    def audit_integration(self, tenant_id: str = "system") -> Tuple[IntegrationHealth, List[PlatformAuditFinding]]:
        subsystems = self.registry.list_all_subsystems()
        findings: List[PlatformAuditFinding] = []

        healthy_count = 0
        total_count = len(subsystems)

        for sub in subsystems:
            if sub.status in [IntegrationHealthStatus.HEALTHY, IntegrationHealthStatus.DEGRADED]:
                healthy_count += 1
            else:
                finding = PlatformAuditFinding(
                    finding_id=f"integration-{sub.subsystem_name.lower().replace(' ', '-')}",
                    tenant_id=tenant_id,
                    rule_id="RULE-INT-001",
                    title=f"Subsystem Integration Unhealthy: '{sub.subsystem_name}'",
                    description=f"Subsystem '{sub.subsystem_name}' (Phase {sub.phase}) reported status {sub.status.value}: {sub.error_message}",
                    severity=(
                        PlatformAuditSeverity.CRITICAL if sub.phase in ["5.51", "5.58"] else PlatformAuditSeverity.HIGH
                    ),
                    subsystem=sub.subsystem_name,
                    affected_component=f"Phase {sub.phase}",
                    root_cause_hypothesis="Provider failure, network partition, or missing initialization.",
                    remediation_suggestion=f"Check logs and provider connectivity for {sub.subsystem_name}.",
                )
                findings.append(finding)

        overall_score = (healthy_count / total_count) * 100.0 if total_count > 0 else 0.0

        if overall_score == 100.0:
            overall_health = IntegrationHealthStatus.HEALTHY
        elif overall_score >= 70.0:
            overall_health = IntegrationHealthStatus.DEGRADED
        else:
            overall_health = IntegrationHealthStatus.UNHEALTHY

        health = IntegrationHealth(
            subsystem_statuses=subsystems,
            provider_statuses=[],
            engine_statuses=[],
            overall_health=overall_health,
            overall_health_score=overall_score,
        )

        return health, findings
