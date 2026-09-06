"""Toxic Combination Intelligence."""

from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class ToxicCombination(BaseModel):
    combination_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    combination_name: str
    conflicting_permissions: List[str]
    severity: str = "HIGH"
    description: str = ""


class ToxicCombinationRisk(BaseModel):
    risk_score: float = 0.0
    detected_combinations: List[ToxicCombination] = Field(default_factory=list)
    has_toxic_combination: bool = False


class ToxicCombinationAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    risk: ToxicCombinationRisk = Field(default_factory=ToxicCombinationRisk)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ToxicCombinationManager:
    """Detects dangerous privilege combinations causing elevated risk."""

    KNOWN_TOXIC_COMBINATIONS = [
        ("data:write", "audit:delete", "CRITICAL", "Data modification combined with audit trail deletion"),
        ("user:create", "role:assign", "HIGH", "User creation combined with arbitrary role assignment"),
        ("billing:modify", "payment:approve", "CRITICAL", "Billing modification combined with payment approval"),
    ]

    def __init__(self) -> None:
        self._assessments: Dict[str, ToxicCombinationAssessment] = {}

    def assess_toxic_combinations(
        self,
        tenant_id: str,
        identity_id: str,
        active_permissions: List[str],
    ) -> ToxicCombinationAssessment:
        detected = []
        for p1, p2, severity, desc in self.KNOWN_TOXIC_COMBINATIONS:
            if p1 in active_permissions and p2 in active_permissions:
                detected.append(
                    ToxicCombination(
                        combination_name=f"{p1} + {p2}",
                        conflicting_permissions=[p1, p2],
                        severity=severity,
                        description=desc,
                    )
                )

        has_toxic = len(detected) > 0
        risk_score = 0.9 if any(tc.severity == "CRITICAL" for tc in detected) else (0.6 if has_toxic else 0.0)

        risk = ToxicCombinationRisk(
            risk_score=risk_score,
            detected_combinations=detected,
            has_toxic_combination=has_toxic,
        )

        assessment = ToxicCombinationAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            risk=risk,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> ToxicCombinationAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
