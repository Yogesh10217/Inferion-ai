"""Tenant-Scoped Architecture Node Registry & Management."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.architecture_platform.exceptions import (
    ArchitectureNodeNotFoundException,
    CrossTenantArchitectureAccessException,
)


class ArchitectureNodeType(str, Enum):
    APPLICATION = "APPLICATION"
    SERVICE = "SERVICE"
    AGENT = "AGENT"
    AGENT_TEAM = "AGENT_TEAM"
    WORKFLOW = "WORKFLOW"
    MODEL = "MODEL"
    KNOWLEDGE_SOURCE = "KNOWLEDGE_SOURCE"
    DATA_ASSET = "DATA_ASSET"
    DATABASE = "DATABASE"
    VECTOR_STORE = "VECTOR_STORE"
    INTEGRATION = "INTEGRATION"
    API = "API"
    TOOL = "TOOL"
    QUEUE = "QUEUE"
    CACHE = "CACHE"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    EXTERNAL_SYSTEM = "EXTERNAL_SYSTEM"


class ArchitectureNodeStatus(str, Enum):
    PROPOSED = "PROPOSED"
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    DEPRECATED = "DEPRECATED"
    DECOMMISSIONED = "DECOMMISSIONED"


class ArchitectureNodeMetadata(BaseModel):
    environment: str = "production"
    owner_id: str = "system"
    owner_email: str = "admin@example.com"
    team: str = "core"
    source_manager: Optional[str] = None
    resource_type: Optional[str] = None
    resource_id: Optional[str] = None
    attributes: Dict[str, Any] = Field(default_factory=dict)


class ArchitectureNode(BaseModel):
    """Universal architecture node representation."""

    tenant_id: str
    node_id: str = Field(default_factory=lambda: f"node_{uuid.uuid4().hex[:12]}")
    name: str
    node_type: ArchitectureNodeType
    status: ArchitectureNodeStatus = ArchitectureNodeStatus.ACTIVE
    metadata: ArchitectureNodeMetadata = Field(default_factory=ArchitectureNodeMetadata)
    tags: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def sanitize_metadata(self) -> None:
        """Sanitize secrets or sensitive parameters in node attributes."""
        secret_keys = {"password", "secret", "token", "api_key", "credentials", "private_key"}
        sanitized_attrs = {}
        for k, v in self.metadata.attributes.items():
            if any(sk in k.lower() for sk in secret_keys):
                sanitized_attrs[k] = "[REDACTED]"
            else:
                sanitized_attrs[k] = v
        self.metadata.attributes = sanitized_attrs


class ArchitectureNodeManager:
    """Manages tenant-scoped architecture node registration and discovery."""

    def __init__(self) -> None:
        self._nodes: Dict[str, ArchitectureNode] = {}  # node_id -> ArchitectureNode

    def register_node(
        self,
        tenant_id: str,
        name: str,
        node_type: ArchitectureNodeType,
        environment: str = "production",
        owner_id: str = "system",
        source_manager: Optional[str] = None,
        resource_id: Optional[str] = None,
        node_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
    ) -> ArchitectureNode:
        nid = node_id or f"node_{uuid.uuid4().hex[:12]}"
        meta = ArchitectureNodeMetadata(
            environment=environment,
            owner_id=owner_id,
            source_manager=source_manager,
            resource_type=node_type.value,
            resource_id=resource_id,
            attributes=attributes or {},
        )
        node = ArchitectureNode(
            tenant_id=tenant_id,
            node_id=nid,
            name=name,
            node_type=node_type,
            metadata=meta,
            tags=tags or [],
        )
        node.sanitize_metadata()
        self._nodes[nid] = node
        return node

    def get_node(self, node_id: str, tenant_id: str) -> ArchitectureNode:
        node = self._nodes.get(node_id)
        if not node:
            raise ArchitectureNodeNotFoundException(node_id=node_id, tenant_id=tenant_id)
        if node.tenant_id != tenant_id and tenant_id != "system":
            raise CrossTenantArchitectureAccessException(request_tenant=tenant_id, target_tenant=node.tenant_id, resource_id=node_id)
        return node

    def list_nodes(
        self,
        tenant_id: str,
        node_type: Optional[ArchitectureNodeType] = None,
        environment: Optional[str] = None,
        status: Optional[ArchitectureNodeStatus] = None,
    ) -> List[ArchitectureNode]:
        nodes = [n for n in self._nodes.values() if n.tenant_id == tenant_id]
        if node_type:
            nodes = [n for n in nodes if n.node_type == node_type]
        if environment:
            nodes = [n for n in nodes if n.metadata.environment == environment]
        if status:
            nodes = [n for n in nodes if n.status == status]
        return nodes

    def update_node_status(self, node_id: str, tenant_id: str, new_status: ArchitectureNodeStatus) -> ArchitectureNode:
        node = self.get_node(node_id, tenant_id)
        node.status = new_status
        node.updated_at = datetime.now(timezone.utc)
        return node
