"""Model Security Posture Intelligence (Phase 5.44)."""

import logging
import hashlib
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class ModelSecurityRisk(str, Enum):
    PROMPT_INJECTION_EXPOSURE = "PROMPT_INJECTION_EXPOSURE"
    DATA_LEAKAGE_RISK = "DATA_LEAKAGE_RISK"
    INSECURE_TOOL_USAGE = "INSECURE_TOOL_USAGE"
    UNSAFE_INTEGRATIONS = "UNSAFE_INTEGRATIONS"
    EXCESSIVE_PERMISSIONS = "EXCESSIVE_PERMISSIONS"


class ModelSecurityEvidence(BaseModel):
    evidence_id: str
    scan_hash: str
    security_intelligence_ref: Optional[str] = None
    sanitized_findings: List[str] = Field(default_factory=list)


class ModelSecurityFinding(BaseModel):
    finding_id: str
    security_risk: ModelSecurityRisk
    severity: str = "HIGH"
    description: str
    evidence: ModelSecurityEvidence


class ModelSecurityAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    security_score: float  # 0.0 - 1.0
    is_secure: bool = True
    findings: List[ModelSecurityFinding] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelSecurityManager:
    """Manages model security posture intelligence reusing security_intelligence and access_intelligence."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ModelSecurityAssessment] = {}

    def assess_security(
        self,
        model_id: str,
        tenant_id: str,
        findings: Optional[List[ModelSecurityFinding]] = None,
    ) -> ModelSecurityAssessment:
        finds = findings or []
        crit = sum(1 for f in finds if f.severity in ["HIGH", "CRITICAL"])
        score = max(0.0, 1.0 - (crit * 0.25) - (len(finds) * 0.05))
        is_sec = score >= 0.85

        assessment = ModelSecurityAssessment(
            assessment_id=f"sec-assess-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            security_score=score,
            is_secure=is_sec,
            findings=finds,
        )

        self._assessments[assessment.assessment_id] = assessment
        logger.info(f"[MODEL SECURITY] Assessed {model_id} (Tenant: {tenant_id}) Score: {score:.2f} Secure: {is_sec}")
        return assessment

    def create_finding(
        self,
        security_risk: ModelSecurityRisk,
        severity: str,
        description: str,
        sec_intel_ref: Optional[str] = None,
    ) -> ModelSecurityFinding:
        fp = hashlib.sha256(f"{security_risk}:{severity}:{description}".encode()).hexdigest()
        evidence = ModelSecurityEvidence(
            evidence_id=f"secevid-{uuid.uuid4().hex[:6]}",
            scan_hash=fp,
            security_intelligence_ref=sec_intel_ref,
        )
        return ModelSecurityFinding(
            finding_id=f"secfind-{uuid.uuid4().hex[:6]}",
            security_risk=security_risk,
            severity=severity,
            description=description,
            evidence=evidence,
        )

    def get_latest_assessment(self, model_id: str, tenant_id: str) -> Optional[ModelSecurityAssessment]:
        matches = [a for a in self._assessments.values() if a.model_id == model_id]
        if not matches:
            return None
        latest = matches[-1]
        if latest.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return latest
