"""Integration Endpoint Intelligence (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException
from app.platform_contracts.redaction import SensitiveDataSanitizer


class EndpointType(str, Enum):
    REST_API = "REST_API"
    GRAPHQL = "GRAPHQL"
    GRPC = "GRPC"
    MESSAGE_QUEUE = "MESSAGE_QUEUE"
    EVENT_STREAM = "EVENT_STREAM"
    DATABASE_QUERY = "DATABASE_QUERY"


class EndpointProtocol(str, Enum):
    HTTP_HTTPS = "HTTP_HTTPS"
    GRPC_PROTO = "GRPC_PROTO"
    AMQP_MQTT = "AMQP_MQTT"
    KAFKA_STREAM = "KAFKA_STREAM"
    JDBC_ODBC = "JDBC_ODBC"


class EndpointClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    PRIVATE_VPC = "PRIVATE_VPC"
    PROTECTED = "PROTECTED"


class EndpointHealth(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    UNREACHABLE = "UNREACHABLE"
    UNKNOWN = "UNKNOWN"


class IntegrationEndpoint(BaseModel):
    """Integration Endpoint Representation."""
    endpoint_id: str = Field(default_factory=lambda: f"ep_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    connector_id: str
    name: str
    endpoint_type: EndpointType
    protocol: EndpointProtocol = EndpointProtocol.HTTP_HTTPS
    classification: EndpointClassification = EndpointClassification.INTERNAL
    health: EndpointHealth = EndpointHealth.HEALTHY
    path_or_topic: str
    sanitized_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class EndpointManager:
    """Manages integration endpoints with sanitized metadata."""

    def __init__(self) -> None:
        self._endpoints: Dict[str, IntegrationEndpoint] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def register_endpoint(
        self,
        tenant_id: str,
        connector_id: str,
        name: str,
        endpoint_type: EndpointType,
        path_or_topic: str,
        protocol: EndpointProtocol = EndpointProtocol.HTTP_HTTPS,
        classification: EndpointClassification = EndpointClassification.INTERNAL,
        raw_metadata: Optional[Dict[str, Any]] = None,
    ) -> IntegrationEndpoint:
        sanitized = self.sanitizer.sanitize(raw_metadata or {})
        ep = IntegrationEndpoint(
            tenant_id=tenant_id,
            connector_id=connector_id,
            name=name,
            endpoint_type=endpoint_type,
            protocol=protocol,
            classification=classification,
            path_or_topic=path_or_topic,
            sanitized_metadata=sanitized,
        )
        self._endpoints[ep.endpoint_id] = ep
        return ep

    def get_endpoint(self, tenant_id: str, endpoint_id: str) -> IntegrationEndpoint:
        ep = self._endpoints.get(endpoint_id)
        if not ep or ep.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return ep

    def list_endpoints(self, tenant_id: str, connector_id: Optional[str] = None) -> List[IntegrationEndpoint]:
        results = [e for e in self._endpoints.values() if e.tenant_id == tenant_id]
        if connector_id:
            results = [e for e in results if e.connector_id == connector_id]
        return results

    def update_health(self, tenant_id: str, endpoint_id: str, health: EndpointHealth) -> IntegrationEndpoint:
        ep = self.get_endpoint(tenant_id, endpoint_id)
        ep.health = health
        ep.updated_at = datetime.now(timezone.utc)
        return ep
