"""Security Asset Definitions & Data Models."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict

from pydantic import BaseModel, Field


class SecurityAssetType(str, Enum):
    AI_MODEL = "AI_MODEL"
    AGENT = "AGENT"
    CONTAINER = "CONTAINER"
    API_ENDPOINT = "API_ENDPOINT"
    DATASET = "DATASET"
    SECRET_REFERENCE = "SECRET_REFERENCE"
    CODE_REPOSITORY = "CODE_REPOSITORY"
    CLOUD_INFRASTRUCTURE = "CLOUD_INFRASTRUCTURE"
    NETWORK_GATEWAY = "NETWORK_GATEWAY"


class SecurityCriticality(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class SecurityAsset(BaseModel):
    """Represents an asset registered for security monitoring and posture analysis."""

    asset_id: str = Field(default_factory=lambda: f"sec-asset-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    name: str
    asset_type: SecurityAssetType
    criticality: SecurityCriticality = SecurityCriticality.MEDIUM
    location: str = "internal"
    owner: str = "security-team"
    tags: Dict[str, str] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
