"""Enterprise Connector Registry (Phase 5.40)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.integration_intelligence.exceptions import CrossTenantIntegrationAccessException
from app.platform_contracts.redaction import SensitiveDataSanitizer


class ConnectorType(str, Enum):
    API = "API"
    SAAS = "SAAS"
    DATABASE = "DATABASE"
    MESSAGE_QUEUE = "MESSAGE_QUEUE"
    ENTERPRISE_APP = "ENTERPRISE_APP"
    INTERNAL_SERVICE = "INTERNAL_SERVICE"
    CLOUD_SERVICE = "CLOUD_SERVICE"


class ConnectorStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEPRECATED = "DEPRECATED"
    DISABLED = "DISABLED"
    MAINTENANCE = "MAINTENANCE"


class ConnectorCapability(str, Enum):
    READ = "READ"
    WRITE = "WRITE"
    STREAM = "STREAM"
    BULK = "BULK"
    TRANSACTIONAL = "TRANSACTIONAL"


class ConnectorReference(BaseModel):
    """Reference pointing to system integration target without storing secrets."""

    external_system_id: str
    provider_name: str
    base_endpoint_url: str
    auth_type: str = "OAUTH2"  # OAUTH2, API_KEY, MUTUAL_TLS, IAM_ROLE
    secret_reference_id: Optional[str] = None  # Reference ID ONLY, NEVER plain secrets


class IntegrationConnector(BaseModel):
    """Enterprise Integration Connector Representation."""

    connector_id: str = Field(default_factory=lambda: f"conn_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    description: str = ""
    connector_type: ConnectorType
    status: ConnectorStatus = ConnectorStatus.ACTIVE
    capabilities: List[ConnectorCapability] = Field(default_factory=list)
    reference: ConnectorReference
    sanitized_metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ConnectorManager:
    """Manages enterprise connector references with zero secret storage."""

    def __init__(self) -> None:
        self._connectors: Dict[str, IntegrationConnector] = {}
        self.sanitizer = SensitiveDataSanitizer()

    def register_connector(
        self,
        tenant_id: str,
        name: str,
        connector_type: ConnectorType,
        external_system_id: str,
        provider_name: str,
        base_endpoint_url: str,
        capabilities: Optional[List[ConnectorCapability]] = None,
        auth_type: str = "OAUTH2",
        secret_reference_id: Optional[str] = None,
        description: str = "",
        raw_metadata: Optional[Dict[str, Any]] = None,
    ) -> IntegrationConnector:
        ref = ConnectorReference(
            external_system_id=external_system_id,
            provider_name=provider_name,
            base_endpoint_url=base_endpoint_url,
            auth_type=auth_type,
            secret_reference_id=secret_reference_id,
        )
        sanitized = self.sanitizer.sanitize(raw_metadata or {})

        conn = IntegrationConnector(
            tenant_id=tenant_id,
            name=name,
            description=description,
            connector_type=connector_type,
            capabilities=capabilities or [ConnectorCapability.READ],
            reference=ref,
            sanitized_metadata=sanitized,
        )
        self._connectors[conn.connector_id] = conn
        return conn

    def get_connector(self, tenant_id: str, connector_id: str) -> IntegrationConnector:
        conn = self._connectors.get(connector_id)
        if not conn or conn.tenant_id != tenant_id:
            raise CrossTenantIntegrationAccessException()
        return conn

    def list_connectors(
        self,
        tenant_id: str,
        connector_type: Optional[ConnectorType] = None,
        status: Optional[ConnectorStatus] = None,
    ) -> List[IntegrationConnector]:
        results = [c for c in self._connectors.values() if c.tenant_id == tenant_id]
        if connector_type:
            results = [c for c in results if c.connector_type == connector_type]
        if status:
            results = [c for c in results if c.status == status]
        return results
