"""Integration Core & Model Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class IntegrationType(str, Enum):
    SAAS = "SAAS"
    DATABASE = "DATABASE"
    COMMUNICATION = "COMMUNICATION"
    COLLABORATION = "COLLABORATION"
    CRM = "CRM"
    ERP = "ERP"
    DEVELOPER_TOOL = "DEVELOPER_TOOL"
    STORAGE = "STORAGE"
    IDENTITY = "IDENTITY"
    MONITORING = "MONITORING"
    PAYMENT = "PAYMENT"
    CUSTOM_API = "CUSTOM_API"
    WEBHOOK = "WEBHOOK"
    PLUGIN = "PLUGIN"
    MCP = "MCP"


class IntegrationStatus(str, Enum):
    DRAFT = "DRAFT"
    CONFIGURED = "CONFIGURED"
    AUTHENTICATING = "AUTHENTICATING"
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    SUSPENDED = "SUSPENDED"
    FAILED = "FAILED"
    DISABLED = "DISABLED"
    ARCHIVED = "ARCHIVED"


class IntegrationCapability(BaseModel):
    name: str
    description: str = ""


class IntegrationConfiguration(BaseModel):
    config_id: str = Field(default_factory=lambda: f"iconf_{uuid.uuid4().hex[:10]}")
    settings: Dict[str, Any] = Field(default_factory=dict)


class IntegrationVersion(BaseModel):


    version_id: str = Field(default_factory=lambda: f"iver_{uuid.uuid4().hex[:10]}")
    version_number: str = "1.0.0"
    capabilities: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=_now)


class Integration(BaseModel):
    integration_id: str = Field(default_factory=lambda: f"integ_{uuid.uuid4().hex[:10]}")
    name: str
    category: IntegrationType = IntegrationType.SAAS
    status: IntegrationStatus = IntegrationStatus.ACTIVE
    tenant_id: str = "global"

    current_version: IntegrationVersion = Field(default_factory=IntegrationVersion)
    config: Dict[str, Any] = Field(default_factory=dict)
    credential_id: Optional[str] = None
    health_status: str = "HEALTHY"

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)
