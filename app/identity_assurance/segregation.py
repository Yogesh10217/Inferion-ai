"""Segregation of Duties (SoD) Intelligence."""

import uuid
from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, Field

from app.identity_assurance.exceptions import CrossTenantIdentityAssuranceException


class SegregationRule(BaseModel):
    rule_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_name: str
    role_a: str
    role_b: str
    description: str = "Conflicting roles prohibited"


class SegregationConflict(BaseModel):
    conflict_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    rule_id: str
    identity_id: str
    conflicting_roles: List[str]
    risk_level: str = "HIGH"


class SegregationAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    identity_id: str
    tenant_id: str
    conflicts: List[SegregationConflict] = Field(default_factory=list)
    has_conflict: bool = False
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SegregationManager:
    """Manages segregation of duties (SoD) rule evaluation."""

    DEFAULT_RULES = [
        SegregationRule(rule_name="Developer vs Deployer", role_a="Developer", role_b="ReleaseManager"),
        SegregationRule(rule_name="Auditor vs Administrator", role_a="Auditor", role_b="GlobalAdmin"),
    ]

    def __init__(self) -> None:
        self._assessments: Dict[str, SegregationAssessment] = {}

    def assess_segregation(
        self,
        tenant_id: str,
        identity_id: str,
        assigned_roles: List[str],
    ) -> SegregationAssessment:
        conflicts = []
        for rule in self.DEFAULT_RULES:
            if rule.role_a in assigned_roles and rule.role_b in assigned_roles:
                conflicts.append(
                    SegregationConflict(
                        rule_id=rule.rule_id,
                        identity_id=identity_id,
                        conflicting_roles=[rule.role_a, rule.role_b],
                        risk_level="HIGH",
                    )
                )

        assessment = SegregationAssessment(
            identity_id=identity_id,
            tenant_id=tenant_id,
            conflicts=conflicts,
            has_conflict=len(conflicts) > 0,
        )
        self._assessments[identity_id] = assessment
        return assessment

    def get_assessment(self, tenant_id: str, identity_id: str) -> SegregationAssessment:
        assessment = self._assessments.get(identity_id)
        if not assessment or assessment.tenant_id != tenant_id:
            raise CrossTenantIdentityAssuranceException()
        return assessment
