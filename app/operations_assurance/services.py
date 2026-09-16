"""Enterprise Service Intelligence."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.operations_assurance.exceptions import (
    CrossTenantOperationsAssuranceException,
)


class ServiceType(str, Enum):
    API = "API"
    API_GATEWAY = "API_GATEWAY"
    MICROSERVICE = "MICROSERVICE"
    DATABASE = "DATABASE"
    DATA_PIPELINE = "DATA_PIPELINE"
    MODEL_SERVICE = "MODEL_SERVICE"
    AI_MODEL_SERVICE = "AI_MODEL_SERVICE"
    AGENT_SERVICE = "AGENT_SERVICE"
    WORKFLOW_ENGINE = "WORKFLOW_ENGINE"
    CACHE = "CACHE"
    STORAGE = "STORAGE"
    EXTERNAL_API = "EXTERNAL_API"


class ServiceStatus(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNHEALTHY = "UNHEALTHY"
    UNKNOWN = "UNKNOWN"
    MAINTENANCE = "MAINTENANCE"


class ServiceTier(str, Enum):
    TIER_0 = "TIER_0"
    TIER_1 = "TIER_1"
    TIER_2 = "TIER_2"
    TIER_3 = "TIER_3"


class ServiceCriticality(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class ServiceOwner(BaseModel):
    team: str = "Platform Ops"
    lead: str = "lead@enterprise.ai"
    escalation_channel: str = "#ops-escalations"


class ServiceMetadata(BaseModel):
    environment: str = "production"
    region: str = "us-east-1"
    version: str = "1.0.0"
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ServiceReference(BaseModel):
    service_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    tenant_id: str
    name: str
    service_type: ServiceType = ServiceType.MICROSERVICE
    status: ServiceStatus = ServiceStatus.HEALTHY
    tier: ServiceTier = ServiceTier.TIER_1
    criticality: ServiceCriticality = ServiceCriticality.HIGH
    owner: ServiceOwner = Field(default_factory=ServiceOwner)
    metadata: ServiceMetadata = Field(default_factory=ServiceMetadata)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    service_id: str
    tenant_id: str
    health_status: ServiceStatus = ServiceStatus.HEALTHY
    reliability_score: float = 0.99
    risk_level: str = "LOW"
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ServiceIntelligenceManager:
    """Manages enterprise service references and assessments with strict tenant isolation."""

    def __init__(self) -> None:
        self._services: Dict[str, ServiceReference] = {}
        self._assessments: Dict[str, ServiceAssessment] = {}

    def register_service(
        self,
        tenant_id: str,
        name: str,
        service_type: ServiceType = ServiceType.MICROSERVICE,
        tier: ServiceTier = ServiceTier.TIER_1,
        criticality: ServiceCriticality = ServiceCriticality.HIGH,
        owner: Optional[ServiceOwner] = None,
        metadata: Optional[ServiceMetadata] = None,
    ) -> ServiceReference:
        service = ServiceReference(
            tenant_id=tenant_id,
            name=name,
            service_type=service_type,
            tier=tier,
            criticality=criticality,
            owner=owner or ServiceOwner(),
            metadata=metadata or ServiceMetadata(),
        )
        self._services[service.service_id] = service
        return service

    def get_service(self, tenant_id: str, service_id: str) -> ServiceReference:
        service = self._services.get(service_id)
        if not service or service.tenant_id != tenant_id:
            raise CrossTenantOperationsAssuranceException()
        return service

    def list_services(
        self,
        tenant_id: str,
        service_type: Optional[ServiceType] = None,
    ) -> List[ServiceReference]:
        res = []
        for s in self._services.values():
            if s.tenant_id == tenant_id:
                if service_type is None or s.service_type == service_type:
                    res.append(s)
        return res
