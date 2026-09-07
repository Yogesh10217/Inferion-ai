"""Service health intelligence evaluating availability, latency, error rate, throughput, dependency health, resource pressure, and incident state."""

from datetime import datetime, timezone
from enum import Enum
from typing import Dict, Any, List, Optional
import uuid
from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import CrossTenantOperationsAssuranceException, ServiceHealthNotFoundException


class ServiceHealthStatus(str, Enum):
    EXCELLENT = "EXCELLENT"
    GOOD = "GOOD"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class ServiceHealthAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    service_id: str
    status: ServiceHealthStatus
    availability_score: float = 1.0
    latency_p99_ms: float = 0.0
    error_rate: float = 0.0
    throughput_tps: float = 0.0
    dependency_health_score: float = 1.0
    resource_pressure: float = 0.0
    incident_count: int = 0
    explanations: List[str] = Field(default_factory=list)
    assessed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceHealthManager:
    """Evaluates and manages enterprise service health intelligence."""

    def __init__(self) -> None:
        self._assessments: Dict[str, Dict[str, ServiceHealthAssessment]] = {}  # tenant_id -> {service_id: assessment}

    def evaluate_health(
        self,
        tenant_id: str,
        service_id: str,
        availability: float = 1.0,
        latency_p99_ms: float = 50.0,
        error_rate: float = 0.0,
        throughput_tps: float = 100.0,
        dependency_health: float = 1.0,
        resource_pressure: float = 0.2,
        active_incidents: int = 0,
    ) -> ServiceHealthAssessment:
        explanations = []

        if active_incidents > 0:
            explanations.append(f"Service has {active_incidents} active incident(s).")
        if error_rate > 0.05:
            explanations.append(f"Elevated error rate: {error_rate * 100:.2f}%.")
        if latency_p99_ms > 500:
            explanations.append(f"High latency p99: {latency_p99_ms:.1f}ms.")
        if resource_pressure > 0.85:
            explanations.append(f"High resource pressure: {resource_pressure * 100:.1f}%.")
        if dependency_health < 0.8:
            explanations.append(f"Degraded dependency health score: {dependency_health:.2f}.")

        if active_incidents > 2 or error_rate > 0.15 or availability < 0.90:
            status = ServiceHealthStatus.CRITICAL
        elif active_incidents > 0 or error_rate > 0.02 or latency_p99_ms > 200 or resource_pressure > 0.8:
            status = ServiceHealthStatus.DEGRADED
        elif error_rate > 0.005 or latency_p99_ms > 100:
            status = ServiceHealthStatus.GOOD
        else:
            status = ServiceHealthStatus.EXCELLENT

        if not explanations:
            explanations.append("Service operating within normal parameters.")

        assessment = ServiceHealthAssessment(
            tenant_id=tenant_id,
            service_id=service_id,
            status=status,
            availability_score=availability,
            latency_p99_ms=latency_p99_ms,
            error_rate=error_rate,
            throughput_tps=throughput_tps,
            dependency_health_score=dependency_health,
            resource_pressure=resource_pressure,
            incident_count=active_incidents,
            explanations=explanations,
        )

        if tenant_id not in self._assessments:
            self._assessments[tenant_id] = {}
        self._assessments[tenant_id][service_id] = assessment
        return assessment

    def get_health(self, tenant_id: str, service_id: str) -> ServiceHealthAssessment:
        if tenant_id not in self._assessments or service_id not in self._assessments[tenant_id]:
            # Check if exists in another tenant to enforce tenant isolation exception without leaking details
            for tid, services in self._assessments.items():
                if tid != tenant_id and service_id in services:
                    raise CrossTenantOperationsAssuranceException("Access denied.")
            raise ServiceHealthNotFoundException("Service health assessment not found.")
        return self._assessments[tenant_id][service_id]
