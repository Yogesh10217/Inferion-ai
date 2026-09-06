"""Model Safety Intelligence (Phase 5.44)."""

import logging
import hashlib
from enum import Enum
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.model_intelligence.exceptions import CrossTenantModelIntelligenceException

logger = logging.getLogger(__name__)


class SafetyRisk(str, Enum):
    TOXICITY = "TOXICITY"
    BIAS = "BIAS"
    HARMFUL_CONTENT = "HARMFUL_CONTENT"
    JAILBREAK_SUSCEPTIBILITY = "JAILBREAK_SUSCEPTIBILITY"
    EXTREMISM = "EXTREMISM"


class SafetyStatus(str, Enum):
    SAFE = "SAFE"
    WARNING = "WARNING"
    UNSAFE = "UNSAFE"


class SafetyEvidence(BaseModel):
    evidence_id: str
    red_teaming_hash: str
    total_prompts_tested: int = 100
    sanitized_metadata: Dict[str, Any] = Field(default_factory=dict)


class SafetyFinding(BaseModel):
    finding_id: str
    safety_risk: SafetyRisk
    severity: str = "HIGH"
    description: str
    evidence: SafetyEvidence


class ModelSafetyAssessment(BaseModel):
    assessment_id: str
    model_id: str
    tenant_id: str
    safety_score: float  # 0.0 - 1.0 (1.0 = completely safe)
    status: SafetyStatus = SafetyStatus.SAFE
    findings: List[SafetyFinding] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ModelSafetyManager:
    """Manages model safety intelligence integrating with security_intelligence, control_assurance, and governance_platform."""

    def __init__(self) -> None:
        self._assessments: Dict[str, ModelSafetyAssessment] = {}

    def evaluate_safety(
        self,
        model_id: str,
        tenant_id: str,
        findings: Optional[List[SafetyFinding]] = None,
        total_prompts_tested: int = 100,
    ) -> ModelSafetyAssessment:
        finds = findings or []
        crit_count = sum(1 for f in finds if f.severity in ["HIGH", "CRITICAL"])
        score = max(0.0, 1.0 - (crit_count * 0.2) - (len(finds) * 0.05))

        status = SafetyStatus.SAFE if score >= 0.9 else (SafetyStatus.WARNING if score >= 0.7 else SafetyStatus.UNSAFE)

        assessment = ModelSafetyAssessment(
            assessment_id=f"safe-assess-{uuid.uuid4().hex[:8]}",
            model_id=model_id,
            tenant_id=tenant_id,
            safety_score=score,
            status=status,
            findings=finds,
        )

        self._assessments[assessment.assessment_id] = assessment
        logger.info(f"[MODEL SAFETY] Evaluated {model_id} (Tenant: {tenant_id}) Score: {score:.2f} Status: {status}")
        return assessment

    def create_finding(
        self,
        safety_risk: SafetyRisk,
        severity: str,
        description: str,
        test_suite_name: str = "red_team_v1",
    ) -> SafetyFinding:
        fp = hashlib.sha256(f"{safety_risk}:{severity}:{test_suite_name}".encode()).hexdigest()
        evidence = SafetyEvidence(
            evidence_id=f"sevid-{uuid.uuid4().hex[:6]}",
            red_teaming_hash=fp,
            sanitized_metadata={"suite": test_suite_name},
        )
        return SafetyFinding(
            finding_id=f"sfind-{uuid.uuid4().hex[:6]}",
            safety_risk=safety_risk,
            severity=severity,
            description=description,
            evidence=evidence,
        )

    def get_latest_assessment(self, model_id: str, tenant_id: str) -> Optional[ModelSafetyAssessment]:
        matches = [a for a in self._assessments.values() if a.model_id == model_id]
        if not matches:
            return None
        latest = matches[-1]
        if latest.tenant_id != tenant_id:
            raise CrossTenantModelIntelligenceException()
        return latest
