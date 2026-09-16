"""Compliance Assurance Reporting & Immutable Reports Subsystem."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.compliance_platform.exceptions import (
    CrossTenantComplianceAccessException,
    ImmutableAssuranceReportException,
)


class AssuranceConclusion(str, Enum):
    ASSURED = "ASSURED"
    PARTIALLY_ASSURED = "PARTIALLY_ASSURED"
    NOT_ASSURED = "NOT_ASSURED"
    INSUFFICIENT_EVIDENCE = "INSUFFICIENT_EVIDENCE"


class AssuranceLevel(str, Enum):
    HIGH = "HIGH"
    MODERATE = "MODERATE"
    LIMITED = "LIMITED"


class ComplianceAssuranceReport(BaseModel):
    report_id: str = Field(default_factory=lambda: f"assure_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    framework_id: str
    conclusion: AssuranceConclusion
    assurance_level: AssuranceLevel = AssuranceLevel.HIGH
    evaluated_requirements_count: int = 0
    passed_requirements_count: int = 0
    failed_requirements_count: int = 0
    evidence_bundle_reference: Optional[str] = None
    report_fingerprint: str
    is_finalized: bool = True
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AssuranceManager:
    """Generates and manages immutable compliance assurance reports."""

    def __init__(self) -> None:
        self._reports: Dict[str, ComplianceAssuranceReport] = {}

    def generate_assurance_report(
        self,
        tenant_id: str,
        framework_id: str,
        conclusion: AssuranceConclusion,
        evaluated_cnt: int = 10,
        passed_cnt: int = 10,
        failed_cnt: int = 0,
        evidence_bundle_ref: Optional[str] = None,
    ) -> ComplianceAssuranceReport:
        canonical_str = json.dumps(
            {
                "tenant": tenant_id,
                "framework": framework_id,
                "conclusion": conclusion.value,
                "passed": passed_cnt,
                "failed": failed_cnt,
                "bundle": evidence_bundle_ref,
            },
            sort_keys=True,
        )
        fingerprint = hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

        report = ComplianceAssuranceReport(
            tenant_id=tenant_id,
            framework_id=framework_id,
            conclusion=conclusion,
            evaluated_requirements_count=evaluated_cnt,
            passed_requirements_count=passed_cnt,
            failed_requirements_count=failed_cnt,
            evidence_bundle_reference=evidence_bundle_ref,
            report_fingerprint=fingerprint,
            is_finalized=True,
        )

        self._reports[report.report_id] = report
        return report

    def get_report(self, report_id: str, tenant_id: str) -> ComplianceAssuranceReport:
        rep = self._reports.get(report_id)
        if not rep:
            raise ImmutableAssuranceReportException(report_id=report_id, tenant_id=tenant_id)
        if rep.tenant_id != tenant_id and tenant_id != "global":
            raise CrossTenantComplianceAccessException(request_tenant=tenant_id, target_tenant=rep.tenant_id, resource_id=report_id)
        return rep
