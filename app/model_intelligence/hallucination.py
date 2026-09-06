"""Hallucination Intelligence Layer (Phase 5.44)."""

import logging
import hashlib
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class HallucinationType(str, Enum):
    UNSUPPORTED_CLAIMS = "UNSUPPORTED_CLAIMS"
    FABRICATED_REFERENCES = "FABRICATED_REFERENCES"
    FACTUAL_INCONSISTENCY = "FACTUAL_INCONSISTENCY"
    GROUNDING_FAILURE = "GROUNDING_FAILURE"
    RETRIEVAL_MISMATCH = "RETRIEVAL_MISMATCH"


class HallucinationSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class HallucinationEvidence(BaseModel):
    evidence_id: str
    prompt_hash: str
    response_hash: str
    context_reference_hash: Optional[str] = None
    sanitized_snippet: str = "[REDACTED_PROMPT_SNIPPET]"


class HallucinationFinding(BaseModel):
    finding_id: str
    hallucination_type: HallucinationType
    severity: HallucinationSeverity
    confidence: float  # 0.0 - 1.0
    evidence: HallucinationEvidence
    description: str


class HallucinationAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    hallucination_rate: float  # e.g., 0.02
    total_evaluated: int
    findings: List[HallucinationFinding] = Field(default_factory=list)
    has_critical_hallucination: bool = False
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class HallucinationManager:
    """Manages hallucination detection and intelligence."""

    def __init__(self) -> None:
        self._assessments: Dict[str, HallucinationAssessment] = {}

    def analyze_hallucinations(
        self,
        model_id: str,
        tenant_id: str,
        total_evaluated: int,
        findings: List[HallucinationFinding],
    ) -> HallucinationAssessment:
        rate = len(findings) / max(total_evaluated, 1)
        has_crit = any(f.severity == HallucinationSeverity.CRITICAL for f in findings)

        assessment = HallucinationAssessment(
            assessment_id=f"hal-assess-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            hallucination_rate=rate,
            total_evaluated=total_evaluated,
            findings=findings,
            has_critical_hallucination=has_crit,
        )

        self._assessments[assessment.assessment_id] = assessment
        logger.info(f"[HALLUCINATION INTELLIGENCE] Analyzed {model_id} (Tenant: {tenant_id}) Rate: {rate:.2%} Critical: {has_crit}")
        return assessment

    def create_finding(
        self,
        hallucination_type: HallucinationType,
        severity: HallucinationSeverity,
        confidence: float,
        description: str,
        prompt_text: str = "sample prompt",
        response_text: str = "sample response",
    ) -> HallucinationFinding:
        p_hash = hashlib.sha256(prompt_text.encode()).hexdigest()
        r_hash = hashlib.sha256(response_text.encode()).hexdigest()

        evidence = HallucinationEvidence(
            evidence_id=f"halevid-{uuid.uuid4().hex[:6]}",
            prompt_hash=p_hash,
            response_hash=r_hash,
            sanitized_snippet="[REDACTED_TEXT]",
        )

        return HallucinationFinding(
            finding_id=f"halfind-{uuid.uuid4().hex[:6]}",
            hallucination_type=hallucination_type,
            severity=severity,
            confidence=confidence,
            evidence=evidence,
            description=description,
        )

    def get_latest_assessment(self, model_id: str, tenant_id: str) -> Optional[HallucinationAssessment]:
        matches = [a for a in self._assessments.values() if a.model_id == model_id]
        if not matches:
            return None
        latest = matches[-1]
        if latest.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return latest
