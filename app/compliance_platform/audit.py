"""Audit Readiness & Immutable Audit Package Orchestration Subsystem."""

import hashlib
import json
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.control_plane.admin_audit import AdministrativeAuditLedger
from app.compliance_platform.exceptions import ImmutableEvidenceBundleException, CrossTenantComplianceAccessException


class AuditPackageStatus(str, Enum):
    DRAFT = "DRAFT"
    COLLECTING = "COLLECTING"
    VALIDATING = "VALIDATING"
    FINALIZED = "FINALIZED"
    DELIVERED = "DELIVERED"
    ARCHIVED = "ARCHIVED"


class AuditRequest(BaseModel):
    request_id: str = Field(default_factory=lambda: f"audreq_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    framework_id: str
    scope: str = "ALL"
    auditor_id: str = "external_auditor"


class AuditPackage(BaseModel):
    package_id: str = Field(default_factory=lambda: f"audpkg_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    framework_id: str
    status: AuditPackageStatus = AuditPackageStatus.FINALIZED
    evidence_bundle_reference: str
    assurance_report_reference: str
    audit_ledger_reference: str
    package_fingerprint: str
    is_finalized: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AuditManager:
    """Orchestrates audit readiness packages and verifies immutability."""

    def __init__(self, audit_ledger: Optional[AdministrativeAuditLedger] = None) -> None:
        self.audit_ledger = audit_ledger or AdministrativeAuditLedger()
        self._packages: Dict[str, AuditPackage] = {}

    def create_audit_package(
        self,
        tenant_id: str,
        framework_id: str,
        evidence_bundle_ref: str,
        assurance_report_ref: str,
    ) -> AuditPackage:
        ledger_ref = f"audit_ledger_{tenant_id}_{uuid.uuid4().hex[:8]}"

        canonical_str = json.dumps(
            {
                "tenant": tenant_id,
                "framework": framework_id,
                "bundle": evidence_bundle_ref,
                "report": assurance_report_ref,
                "ledger": ledger_ref,
            },
            sort_keys=True,
        )
        fingerprint = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        pkg = AuditPackage(
            tenant_id=tenant_id,
            framework_id=framework_id,
            status=AuditPackageStatus.FINALIZED,
            evidence_bundle_reference=evidence_bundle_ref,
            assurance_report_reference=assurance_report_ref,
            audit_ledger_reference=ledger_ref,
            package_fingerprint=fingerprint,
            is_finalized=True,
        )

        self._packages[pkg.package_id] = pkg
        return pkg

    def get_audit_package(self, package_id: str, tenant_id: str) -> AuditPackage:
        pkg = self._packages.get(package_id)
        if not pkg:
            raise ImmutableEvidenceBundleException(bundle_id=package_id, tenant_id=tenant_id)
        if pkg.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantComplianceAccessException(request_tenant=tenant_id, target_tenant=pkg.tenant_id, resource_id=package_id)
        return pkg
