"""
Engine Connectivity Audit.
Validates whether subsystem engines are properly instantiated, invoked, and connected in execution pipelines.
"""

from typing import List, Tuple

from app.platform_hardening.models import (
    EngineConnectionStatus,
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class EngineConnectivityAudit:
    """Audits managers across all 8 phases to detect dead engines, manager bypasses, and disconnected pipelines."""

    def audit_engine_connectivity(
        self, engine_statuses: List[EngineConnectionStatus], tenant_id: str = "system"
    ) -> Tuple[List[EngineConnectionStatus], List[PlatformAuditFinding]]:
        findings: List[PlatformAuditFinding] = []

        for status in engine_statuses:
            if not status.is_instantiated:
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"eng-uninstantiated-{status.engine_name}",
                        tenant_id=tenant_id,
                        rule_id="RULE-ENG-001",
                        title=f"Engine Not Instantiated: '{status.engine_name}'",
                        description=f"Engine '{status.engine_name}' in subsystem '{status.subsystem_name}' is declared but not instantiated by Manager.",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem=status.subsystem_name,
                        affected_component=status.engine_name,
                        remediation_suggestion=f"Instantiate '{status.engine_name}' in '{status.subsystem_name}' Manager __init__.",
                    )
                )

            elif not status.is_called:
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"eng-dead-{status.engine_name}",
                        tenant_id=tenant_id,
                        rule_id="RULE-ENG-002",
                        title=f"Dead Engine Detected: '{status.engine_name}'",
                        description=f"Engine '{status.engine_name}' in '{status.subsystem_name}' is instantiated but never invoked in execution pipeline.",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem=status.subsystem_name,
                        affected_component=status.engine_name,
                        root_cause_hypothesis="Engine method call was commented out or bypassed during pipeline modification.",
                        remediation_suggestion=f"Wire '{status.engine_name}' into main orchestration method of '{status.subsystem_name}' Manager.",
                    )
                )

            if status.manager_bypass_detected:
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"eng-bypass-{status.engine_name}",
                        tenant_id=tenant_id,
                        rule_id="RULE-ENG-003",
                        title=f"Manager Bypass Anti-Pattern: '{status.engine_name}'",
                        description=f"Manager in '{status.subsystem_name}' directly invokes repository methods bypassing engine '{status.engine_name}'.",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem=status.subsystem_name,
                        affected_component=status.engine_name,
                        remediation_suggestion="Route repository mutations through engine business logic.",
                    )
                )

        return engine_statuses, findings
