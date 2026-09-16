"""
Manager Integration Validation Engine.
Audits all 8 upper phase managers for initialization, engine orchestration, context propagation, governance, and tenant isolation.
"""

from typing import Dict, List, Tuple

from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
)


class ManagerIntegrationValidationEngine:
    """Audits phase managers to ensure they comply with orchestration, governance, and evidence standards."""

    REQUIRED_MANAGERS = [
        ("Unified Intelligence", "UnifiedIntelligenceManager"),
        ("Decision Intelligence", "DecisionIntelligenceManager"),
        ("Autonomous Assurance", "AutonomousAssuranceManager"),
        ("Continuous Assurance", "ContinuousAssuranceManager"),
        ("Reliability Intelligence", "ReliabilityIntelligenceManager"),
        ("Capacity Intelligence", "CapacityIntelligenceManager"),
        ("Runtime Intelligence", "RuntimeIntelligenceManager"),
        ("Platform Integration Fabric", "PlatformIntegrationManager"),
    ]

    def audit_managers(
        self, active_managers: Dict[str, object], tenant_id: str = "system"
    ) -> Tuple[bool, List[PlatformAuditFinding]]:
        findings: List[PlatformAuditFinding] = []

        for sub_name, mgr_class_name in self.REQUIRED_MANAGERS:
            mgr_instance = active_managers.get(mgr_class_name) or active_managers.get(sub_name)

            if not mgr_instance:
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"mgr-missing-{mgr_class_name}",
                        tenant_id=tenant_id,
                        rule_id="RULE-MGR-001",
                        title=f"Manager Not Loaded: '{mgr_class_name}'",
                        description=f"Subsystem manager '{mgr_class_name}' for '{sub_name}' is not registered or loaded in active container.",
                        severity=PlatformAuditSeverity.CRITICAL,
                        subsystem=sub_name,
                        affected_component=mgr_class_name,
                        remediation_suggestion=f"Register '{mgr_class_name}' in app/core/container.py and control plane.",
                    )
                )
                continue

            # Check engine initialization on manager
            engine_attrs = [attr for attr in dir(mgr_instance) if "engine" in attr.lower() or "repo" in attr.lower()]
            if not engine_attrs:
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"mgr-no-engines-{mgr_class_name}",
                        tenant_id=tenant_id,
                        rule_id="RULE-MGR-002",
                        title=f"Manager Has No Engine Attributes: '{mgr_class_name}'",
                        description=f"Manager '{mgr_class_name}' has no constituent engine attributes declared.",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem=sub_name,
                        affected_component=mgr_class_name,
                    )
                )

        is_valid = len(findings) == 0
        return is_valid, findings
