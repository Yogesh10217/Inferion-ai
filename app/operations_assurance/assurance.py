"""Continuous operations assurance scoring across Service health, Reliability, Availability, Performance, Capacity, Incidents, Dependencies, and Governance."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Dict, List

from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException


class AssuranceDimension(str, Enum):
    SERVICE_HEALTH = "SERVICE_HEALTH"
    RELIABILITY = "RELIABILITY"
    AVAILABILITY = "AVAILABILITY"
    PERFORMANCE = "PERFORMANCE"
    CAPACITY = "CAPACITY"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    DEPENDENCY_HEALTH = "DEPENDENCY_HEALTH"
    GOVERNANCE = "GOVERNANCE"


class AssuranceStatus(str, Enum):
    OPTIMAL = "OPTIMAL"
    SATISFACTORY = "SATISFACTORY"
    NEEDS_ATTENTION = "NEEDS_ATTENTION"
    CRITICAL_RISK = "CRITICAL_RISK"


class AssuranceFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    dimension: AssuranceDimension
    severity: str = "MEDIUM"
    description: str
    impact: str = ""


class OperationsAssuranceScore(BaseModel):
    score_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    overall_score: float = 0.95
    status: AssuranceStatus = AssuranceStatus.OPTIMAL
    dimension_scores: Dict[AssuranceDimension, float] = Field(default_factory=dict)
    findings: List[AssuranceFinding] = Field(default_factory=list)
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsAssuranceEngine:
    """Computes explainable, continuous operations assurance scores for enterprise services."""

    def __init__(self) -> None:
        self._scores: Dict[str, Dict[str, OperationsAssuranceScore]] = {}  # tenant_id -> {service_id: score}

    def compute_assurance_score(
        self,
        tenant_id: str,
        service_id: str,
        health_score: float = 1.0,
        reliability_score: float = 0.95,
        availability_score: float = 0.999,
        performance_score: float = 0.95,
        capacity_score: float = 0.9,
        incident_score: float = 1.0,
        dependency_score: float = 0.95,
        governance_score: float = 1.0,
    ) -> OperationsAssuranceScore:
        dim_scores = {
            AssuranceDimension.SERVICE_HEALTH: health_score,
            AssuranceDimension.RELIABILITY: reliability_score,
            AssuranceDimension.AVAILABILITY: availability_score,
            AssuranceDimension.PERFORMANCE: performance_score,
            AssuranceDimension.CAPACITY: capacity_score,
            AssuranceDimension.INCIDENT_RESPONSE: incident_score,
            AssuranceDimension.DEPENDENCY_HEALTH: dependency_score,
            AssuranceDimension.GOVERNANCE: governance_score,
        }
        overall = sum(dim_scores.values()) / len(dim_scores)

        findings = []
        if health_score < 0.8:
            findings.append(
                AssuranceFinding(
                    dimension=AssuranceDimension.SERVICE_HEALTH,
                    severity="HIGH",
                    description="Service health is degraded.",
                )
            )
        if capacity_score < 0.7:
            findings.append(
                AssuranceFinding(
                    dimension=AssuranceDimension.CAPACITY,
                    severity="HIGH",
                    description="Capacity is under pressure.",
                )
            )

        if overall >= 0.9:
            status = AssuranceStatus.OPTIMAL
        elif overall >= 0.8:
            status = AssuranceStatus.SATISFACTORY
        elif overall >= 0.6:
            status = AssuranceStatus.NEEDS_ATTENTION
        else:
            status = AssuranceStatus.CRITICAL_RISK

        score = OperationsAssuranceScore(
            tenant_id=tenant_id,
            service_id=service_id,
            overall_score=round(overall, 4),
            status=status,
            dimension_scores=dim_scores,
            findings=findings,
        )

        if tenant_id not in self._scores:
            self._scores[tenant_id] = {}
        self._scores[tenant_id][service_id] = score
        return score

    def get_assurance_score(self, tenant_id: str, service_id: str) -> OperationsAssuranceScore:
        if tenant_id not in self._scores or service_id not in self._scores[tenant_id]:
            for tid, scs in self._scores.items():
                if tid != tenant_id and service_id in scs:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise CrossTenantOperationsAssuranceException("Assurance score not found.")
        return self._scores[tenant_id][service_id]
