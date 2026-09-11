"""
Provider Integration Audit Engine.
Validates provider registration, protocol compliance, timeout isolation, and contract enforcement.
"""

from typing import List, Tuple
from app.platform_hardening.models import (
    PlatformAuditFinding,
    PlatformAuditSeverity,
    ProviderIntegrationStatus,
)
from app.platform_hardening.providers import PlatformHardeningProviderRegistry


class ProviderIntegrationAuditEngine:
    """Audits registered providers for protocol compliance, timeout safety, and fault isolation."""

    def __init__(self, registry: PlatformHardeningProviderRegistry):
        self.registry = registry

    def audit_providers(self, tenant_id: str = "system") -> Tuple[List[ProviderIntegrationStatus], List[PlatformAuditFinding]]:
        provider_ids = self.registry.list_registered_providers()
        statuses: List[ProviderIntegrationStatus] = []
        findings: List[PlatformAuditFinding] = []

        for pid in provider_ids:
            status = self.registry.check_provider_health(pid)
            statuses.append(status)

            if not status.is_registered:
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"provider-unregistered-{pid}",
                        tenant_id=tenant_id,
                        rule_id="RULE-PROV-001",
                        title=f"Provider Not Registered: '{pid}'",
                        description=f"Provider '{pid}' is not properly registered in provider registry.",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem=pid,
                        affected_component="ProviderRegistry",
                        remediation_suggestion=f"Register provider instance for {pid} in container startup.",
                    )
                )

            if not status.contract_valid:
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"provider-contract-{pid}",
                        tenant_id=tenant_id,
                        rule_id="RULE-PROV-002",
                        title=f"Provider Contract Violation: '{pid}'",
                        description=f"Provider '{pid}' violates PlatformHardeningProvider protocol methods.",
                        severity=PlatformAuditSeverity.CRITICAL,
                        subsystem=pid,
                        affected_component=pid,
                        remediation_suggestion=f"Implement missing protocol methods for {pid}.",
                    )
                )

            if not status.is_healthy:
                findings.append(
                    PlatformAuditFinding(
                        finding_id=f"provider-unhealthy-{pid}",
                        tenant_id=tenant_id,
                        rule_id="RULE-PROV-003",
                        title=f"Provider Unhealthy: '{pid}'",
                        description=f"Provider '{pid}' health check failed: {status.error_detail}",
                        severity=PlatformAuditSeverity.HIGH,
                        subsystem=pid,
                        affected_component=pid,
                        remediation_suggestion=f"Inspect error logs for provider {pid}.",
                    )
                )

        return statuses, findings
