"""Enterprise Compliance Posture Subsystem."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class PostureDimension(str, Enum):
    CONTROL_COVERAGE = "CONTROL_COVERAGE"
    CONTROL_EFFECTIVENESS = "CONTROL_EFFECTIVENESS"
    EVIDENCE_FRESHNESS = "EVIDENCE_FRESHNESS"
    ASSESSMENT_RESULTS = "ASSESSMENT_RESULTS"
    OPEN_FINDINGS = "OPEN_FINDINGS"
    RISK_EXPOSURE = "RISK_EXPOSURE"
    ATTESTATION_STATUS = "ATTESTATION_STATUS"
    EXCEPTION_EXPOSURE = "EXCEPTION_EXPOSURE"
    DATA_COMPLIANCE = "DATA_COMPLIANCE"
    ARCHITECTURE_COMPLIANCE = "ARCHITECTURE_COMPLIANCE"
    OPERATIONS_COMPLIANCE = "OPERATIONS_COMPLIANCE"
    AI_GOVERNANCE_COMPLIANCE = "AI_GOVERNANCE_COMPLIANCE"


class PostureBand(str, Enum):
    HIGH_ASSURANCE = "HIGH_ASSURANCE"  # 90-100
    ASSURED = "ASSURED"  # 70-89
    DEGRADED = "DEGRADED"  # 50-69
    NON_COMPLIANT = "NON_COMPLIANT"  # <50


class CompliancePosture(BaseModel):
    posture_id: str = Field(default_factory=lambda: f"posture_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    overall_score: float
    posture_band: PostureBand
    dimension_scores: Dict[PostureDimension, float] = Field(default_factory=dict)
    has_critical_failure: bool = False
    critical_failures: List[str] = Field(default_factory=list)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class CompliancePostureManager:
    """Calculates enterprise compliance posture scores while ensuring critical failures remain visible."""

    def __init__(self) -> None:
        self._posture_cache: Dict[str, CompliancePosture] = {}

    def calculate_posture(
        self,
        tenant_id: str,
        control_coverage: float = 90.0,
        control_effectiveness: float = 90.0,
        evidence_freshness: float = 95.0,
        assessment_results: float = 90.0,
        open_findings_penalty: float = 0.0,
        has_critical_finding: bool = False,
        critical_finding_details: Optional[List[str]] = None,
    ) -> CompliancePosture:
        dim_scores = {
            PostureDimension.CONTROL_COVERAGE: control_coverage,
            PostureDimension.CONTROL_EFFECTIVENESS: control_effectiveness,
            PostureDimension.EVIDENCE_FRESHNESS: evidence_freshness,
            PostureDimension.ASSESSMENT_RESULTS: assessment_results,
            PostureDimension.OPEN_FINDINGS: max(0.0, 100.0 - open_findings_penalty),
            PostureDimension.RISK_EXPOSURE: 90.0,
            PostureDimension.ATTESTATION_STATUS: 95.0,
            PostureDimension.EXCEPTION_EXPOSURE: 90.0,
            PostureDimension.DATA_COMPLIANCE: 95.0,
            PostureDimension.ARCHITECTURE_COMPLIANCE: 90.0,
            PostureDimension.OPERATIONS_COMPLIANCE: 95.0,
            PostureDimension.AI_GOVERNANCE_COMPLIANCE: 95.0,
        }

        weights = {dim: 1.0 / len(dim_scores) for dim in dim_scores}
        overall = sum(dim_scores[dim] * weights[dim] for dim in dim_scores)

        # Critical failure override
        if has_critical_finding:
            overall = min(49.0, overall)
            band = PostureBand.NON_COMPLIANT
        elif overall >= 90.0:
            band = PostureBand.HIGH_ASSURANCE
        elif overall >= 70.0:
            band = PostureBand.ASSURED
        elif overall >= 50.0:
            band = PostureBand.DEGRADED
        else:
            band = PostureBand.NON_COMPLIANT

        posture = CompliancePosture(
            tenant_id=tenant_id,
            overall_score=overall,
            posture_band=band,
            dimension_scores=dim_scores,
            has_critical_failure=has_critical_finding,
            critical_failures=critical_finding_details
            or ([] if not has_critical_finding else ["Critical Compliance Finding Active"]),
        )
        self._posture_cache[tenant_id] = posture
        return posture

    def get_posture(self, tenant_id: str) -> CompliancePosture:
        if tenant_id in self._posture_cache:
            return self._posture_cache[tenant_id]
        return self.calculate_posture(tenant_id)
