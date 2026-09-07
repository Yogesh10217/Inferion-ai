"""Advisory capacity intelligence for CPU, Memory, Storage, Network, Request volume, AI inference capacity, and Agent execution capacity."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CapacityAssessmentException, CrossTenantOperationsAssuranceException


class CapacityResourceType(str, Enum):
    CPU = "CPU"
    MEMORY = "MEMORY"
    STORAGE = "STORAGE"
    NETWORK = "NETWORK"
    REQUEST_VOLUME = "REQUEST_VOLUME"
    AI_INFERENCE_CAPACITY = "AI_INFERENCE_CAPACITY"
    AGENT_EXECUTION_CAPACITY = "AGENT_EXECUTION_CAPACITY"


class CapacityRiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class CapacityAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    resource_type: CapacityResourceType
    current_utilization: float  # 0.0 to 1.0
    projected_utilization: float  # 0.0 to 1.0
    risk_level: CapacityRiskLevel
    advisory_recommendation: str
    auto_execute: bool = False  # Mandatory invariant: advisory only!
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class OperationsCapacityEngine:
    """Evaluates resource capacity risks and produces advisory capacity guidance."""

    def __init__(self) -> None:
        self._assessments: Dict[str, Dict[str, CapacityAssessment]] = {}  # tenant_id -> {assessment_id: assessment}

    def evaluate_capacity(
        self,
        tenant_id: str,
        service_id: str,
        resource_type: CapacityResourceType,
        current_utilization: float,
        projected_utilization: float,
    ) -> CapacityAssessment:
        if projected_utilization >= 0.90:
            risk = CapacityRiskLevel.CRITICAL
            rec = f"Advisory: {resource_type.value} projected utilization is at {projected_utilization * 100:.1f}%. Recommend scaling review."
        elif projected_utilization >= 0.75:
            risk = CapacityRiskLevel.HIGH
            rec = f"Advisory: {resource_type.value} projected utilization is at {projected_utilization * 100:.1f}%. Monitor closely."
        elif projected_utilization >= 0.50:
            risk = CapacityRiskLevel.MEDIUM
            rec = f"Advisory: {resource_type.value} utilization moderate ({projected_utilization * 100:.1f}%)."
        else:
            risk = CapacityRiskLevel.LOW
            rec = f"Advisory: {resource_type.value} utilization optimal."

        assessment = CapacityAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            resource_type=resource_type,
            current_utilization=current_utilization,
            projected_utilization=projected_utilization,
            risk_level=risk,
            advisory_recommendation=rec,
            auto_execute=False,  # MUST NEVER auto-scale directly!
        )

        if tenant_id not in self._assessments:
            self._assessments[tenant_id] = {}
        self._assessments[tenant_id][assessment.assessment_id] = assessment
        return assessment

    def list_capacity_assessments(self, tenant_id: str, service_id: Optional[str] = None) -> List[CapacityAssessment]:
        tenant_assessments = self._assessments.get(tenant_id, {})
        if service_id:
            return [a for a in tenant_assessments.values() if a.service_id == service_id]
        return list(tenant_assessments.values())
