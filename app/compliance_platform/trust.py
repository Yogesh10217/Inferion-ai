"""Compliance Assurance Confidence & Trust Engine."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field


class ComplianceTrustDimension(str, Enum):
    EVIDENCE_INTEGRITY = "EVIDENCE_INTEGRITY"
    EVIDENCE_FRESHNESS = "EVIDENCE_FRESHNESS"
    CONTROL_EFFECTIVENESS = "CONTROL_EFFECTIVENESS"
    ASSESSMENT_CONFIDENCE = "ASSESSMENT_CONFIDENCE"
    AUDIT_TRAIL_COMPLETENESS = "AUDIT_TRAIL_COMPLETENESS"
    ATTESTATION_RELIABILITY = "ATTESTATION_RELIABILITY"
    REMEDIATION_VERIFICATION = "REMEDIATION_VERIFICATION"
    RISK_ALIGNMENT = "RISK_ALIGNMENT"


class ComplianceTrustBand(str, Enum):
    HIGH_ASSURANCE = "HIGH_ASSURANCE"  # 90-100
    ASSURED = "ASSURED"               # 70-89
    RESTRICTED = "RESTRICTED"         # 50-69
    UNTRUSTED = "UNTRUSTED"           # <50


class ComplianceTrustScore(BaseModel):
    score_id: str = Field(default_factory=lambda: f"comptrust_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    overall_score: float
    trust_band: ComplianceTrustBand
    dimension_scores: Dict[ComplianceTrustDimension, float] = Field(default_factory=dict)
    calculated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ComplianceTrustEngine:
    """Calculates multidimensional compliance confidence and trust scores."""

    def __init__(self) -> None:
        self._trust_cache: Dict[str, ComplianceTrustScore] = {}

    def calculate_trust_score(
        self,
        tenant_id: str,
        evidence_integrity: float = 100.0,
        evidence_freshness: float = 95.0,
        control_effectiveness: float = 90.0,
        assessment_confidence: float = 90.0,
        audit_completeness: float = 95.0,
        attestation_reliability: float = 90.0,
        remediation_verification: float = 90.0,
        risk_alignment: float = 90.0,
    ) -> ComplianceTrustScore:
        dim_scores = {
            ComplianceTrustDimension.EVIDENCE_INTEGRITY: evidence_integrity,
            ComplianceTrustDimension.EVIDENCE_FRESHNESS: evidence_freshness,
            ComplianceTrustDimension.CONTROL_EFFECTIVENESS: control_effectiveness,
            ComplianceTrustDimension.ASSESSMENT_CONFIDENCE: assessment_confidence,
            ComplianceTrustDimension.AUDIT_TRAIL_COMPLETENESS: audit_completeness,
            ComplianceTrustDimension.ATTESTATION_RELIABILITY: attestation_reliability,
            ComplianceTrustDimension.REMEDIATION_VERIFICATION: remediation_verification,
            ComplianceTrustDimension.RISK_ALIGNMENT: risk_alignment,
        }

        overall = sum(dim_scores.values()) / len(dim_scores)
        overall = max(0.0, min(100.0, overall))

        if overall >= 90.0:
            band = ComplianceTrustBand.HIGH_ASSURANCE
        elif overall >= 70.0:
            band = ComplianceTrustBand.ASSURED
        elif overall >= 50.0:
            band = ComplianceTrustBand.RESTRICTED
        else:
            band = ComplianceTrustBand.UNTRUSTED

        score = ComplianceTrustScore(
            tenant_id=tenant_id,
            overall_score=overall,
            trust_band=band,
            dimension_scores=dim_scores,
        )
        self._trust_cache[tenant_id] = score
        return score

    def get_trust_score(self, tenant_id: str) -> ComplianceTrustScore:
        if tenant_id in self._trust_cache:
            return self._trust_cache[tenant_id]
        return self.calculate_trust_score(tenant_id)
