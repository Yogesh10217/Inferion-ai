"""
Thread-safe, tenant-isolated repositories for Platform Hardening, Audits & Certification.
"""

from threading import RLock
from typing import Dict, List, Optional

from app.platform_hardening.exceptions import (
    CrossTenantPlatformHardeningException,
    ImmutablePlatformAuditRecordException,
)
from app.platform_hardening.models import (
    CertificationEvidence,
    IntegrationHealth,
    PlatformAuditFinding,
    PlatformAuditResult,
    PlatformCertification,
    RemediationRecommendation,
)


class PlatformAuditRepository:
    """Thread-safe, tenant-isolated repository for platform audit results."""

    def __init__(self):
        self._lock = RLock()
        self._audits: Dict[str, PlatformAuditResult] = {}
        self._sealed_audits: set = set()

    def save(self, tenant_id: str, audit: PlatformAuditResult) -> PlatformAuditResult:
        with self._lock:
            if audit.tenant_id != tenant_id:
                raise CrossTenantPlatformHardeningException()
            if audit.audit_id in self._sealed_audits:
                raise ImmutablePlatformAuditRecordException()
            self._audits[audit.audit_id] = audit
            return audit

    def get(self, tenant_id: str, audit_id: str) -> Optional[PlatformAuditResult]:
        with self._lock:
            audit = self._audits.get(audit_id)
            if audit is None:
                return None
            if audit.tenant_id != tenant_id:
                raise CrossTenantPlatformHardeningException()
            return audit

    def seal(self, tenant_id: str, audit_id: str):
        with self._lock:
            audit = self.get(tenant_id, audit_id)
            if audit:
                self._sealed_audits.add(audit_id)

    def list_by_tenant(self, tenant_id: str) -> List[PlatformAuditResult]:
        with self._lock:
            return [a for a in self._audits.values() if a.tenant_id == tenant_id]


class AuditFindingRepository:
    """Thread-safe, tenant-isolated repository for audit findings."""

    def __init__(self):
        self._lock = RLock()
        self._findings: Dict[str, PlatformAuditFinding] = {}

    def save(self, tenant_id: str, finding: PlatformAuditFinding) -> PlatformAuditFinding:
        with self._lock:
            if finding.tenant_id != tenant_id:
                raise CrossTenantPlatformHardeningException()
            self._findings[finding.finding_id] = finding
            return finding

    def list_by_tenant(self, tenant_id: str) -> List[PlatformAuditFinding]:
        with self._lock:
            return [f for f in self._findings.values() if f.tenant_id == tenant_id]

    def list_by_audit(self, tenant_id: str, audit_id: str) -> List[PlatformAuditFinding]:
        with self._lock:
            return [
                f
                for f in self._findings.values()
                if f.tenant_id == tenant_id and f.metadata.get("audit_id") == audit_id
            ]


class IntegrationHealthRepository:
    def __init__(self):
        self._lock = RLock()
        self._health: Dict[str, IntegrationHealth] = {}

    def save(self, tenant_id: str, health: IntegrationHealth) -> IntegrationHealth:
        with self._lock:
            self._health[tenant_id] = health
            return health

    def get(self, tenant_id: str) -> Optional[IntegrationHealth]:
        with self._lock:
            return self._health.get(tenant_id)


class TraceValidationRepository:
    def __init__(self):
        self._lock = RLock()
        self._traces: Dict[str, dict] = {}

    def save(self, tenant_id: str, trace_id: str, data: dict):
        with self._lock:
            if data.get("tenant_id") and data.get("tenant_id") != tenant_id:
                raise CrossTenantPlatformHardeningException()
            self._traces[f"{tenant_id}:{trace_id}"] = data

    def get(self, tenant_id: str, trace_id: str) -> Optional[dict]:
        with self._lock:
            return self._traces.get(f"{tenant_id}:{trace_id}")


class LineageValidationRepository:
    def __init__(self):
        self._lock = RLock()
        self._lineages: Dict[str, dict] = {}

    def save(self, tenant_id: str, lineage_id: str, data: dict):
        with self._lock:
            self._lineages[f"{tenant_id}:{lineage_id}"] = data

    def get(self, tenant_id: str, lineage_id: str) -> Optional[dict]:
        with self._lock:
            return self._lineages.get(f"{tenant_id}:{lineage_id}")


class GovernanceValidationRepository:
    def __init__(self):
        self._lock = RLock()
        self._gov: Dict[str, dict] = {}

    def save(self, tenant_id: str, gov_id: str, data: dict):
        with self._lock:
            self._gov[f"{tenant_id}:{gov_id}"] = data

    def get(self, tenant_id: str, gov_id: str) -> Optional[dict]:
        with self._lock:
            return self._gov.get(f"{tenant_id}:{gov_id}")


class DelegationValidationRepository:
    def __init__(self):
        self._lock = RLock()
        self._delegations: Dict[str, dict] = {}

    def save(self, tenant_id: str, delegation_id: str, data: dict):
        with self._lock:
            if data.get("tenant_id") and data.get("tenant_id") != tenant_id:
                raise CrossTenantPlatformHardeningException()
            self._delegations[f"{tenant_id}:{delegation_id}"] = data

    def get(self, tenant_id: str, delegation_id: str) -> Optional[dict]:
        with self._lock:
            return self._delegations.get(f"{tenant_id}:{delegation_id}")


class VerificationValidationRepository:
    def __init__(self):
        self._lock = RLock()
        self._verifications: Dict[str, dict] = {}

    def save(self, tenant_id: str, ver_id: str, data: dict):
        with self._lock:
            self._verifications[f"{tenant_id}:{ver_id}"] = data

    def get(self, tenant_id: str, ver_id: str) -> Optional[dict]:
        with self._lock:
            return self._verifications.get(f"{tenant_id}:{ver_id}")


class CertificationRepository:
    def __init__(self):
        self._lock = RLock()
        self._certifications: Dict[str, PlatformCertification] = {}

    def save(self, tenant_id: str, cert: PlatformCertification) -> PlatformCertification:
        with self._lock:
            if cert.tenant_id != tenant_id:
                raise CrossTenantPlatformHardeningException()
            self._certifications[cert.certification_id] = cert
            return cert

    def get_latest(self, tenant_id: str) -> Optional[PlatformCertification]:
        with self._lock:
            tenant_certs = [c for c in self._certifications.values() if c.tenant_id == tenant_id]
            if not tenant_certs:
                return None
            return max(tenant_certs, key=lambda x: x.certified_at)


class RemediationRepository:
    def __init__(self):
        self._lock = RLock()
        self._remediations: Dict[str, RemediationRecommendation] = {}

    def save(self, tenant_id: str, rem: RemediationRecommendation) -> RemediationRecommendation:
        with self._lock:
            if rem.tenant_id != tenant_id:
                raise CrossTenantPlatformHardeningException()
            self._remediations[rem.remediation_id] = rem
            return rem

    def list_by_tenant(self, tenant_id: str) -> List[RemediationRecommendation]:
        with self._lock:
            return [r for r in self._remediations.values() if r.tenant_id == tenant_id]


class EvidenceRepository:
    def __init__(self):
        self._lock = RLock()
        self._evidence: Dict[str, CertificationEvidence] = {}

    def save(self, tenant_id: str, ev: CertificationEvidence) -> CertificationEvidence:
        with self._lock:
            if ev.tenant_id != tenant_id:
                raise CrossTenantPlatformHardeningException()
            self._evidence[ev.evidence_id] = ev
            return ev

    def get(self, tenant_id: str, evidence_id: str) -> Optional[CertificationEvidence]:
        with self._lock:
            ev = self._evidence.get(evidence_id)
            if ev and ev.tenant_id != tenant_id:
                raise CrossTenantPlatformHardeningException()
            return ev


class SnapshotRepository:
    def __init__(self):
        self._lock = RLock()
        self._snapshots: Dict[str, dict] = {}

    def save(self, tenant_id: str, snapshot_id: str, data: dict):
        with self._lock:
            if data.get("tenant_id") and data.get("tenant_id") != tenant_id:
                raise CrossTenantPlatformHardeningException()
            self._snapshots[f"{tenant_id}:{snapshot_id}"] = data

    def get(self, tenant_id: str, snapshot_id: str) -> Optional[dict]:
        with self._lock:
            return self._snapshots.get(f"{tenant_id}:{snapshot_id}")
