"""Enterprise Security Asset Registry Subsystem (Phase 5.32)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.architecture_platform.manager import ArchitecturePlatformManager
from app.platform_contracts.redaction import SensitiveDataSanitizer
from app.security_intelligence.exceptions import CrossTenantSecurityAccessException, SecurityIntelligenceException


class SecurityAssetType(str, Enum):
    APPLICATION = "APPLICATION"
    SERVICE = "SERVICE"
    API = "API"
    MODEL = "MODEL"
    MODEL_GATEWAY = "MODEL_GATEWAY"
    AGENT = "AGENT"

    WORKFLOW = "WORKFLOW"
    DATABASE = "DATABASE"
    DATASET = "DATASET"
    VECTOR_STORE = "VECTOR_STORE"
    INTEGRATION = "INTEGRATION"
    TOOL = "TOOL"
    CLOUD_RESOURCE = "CLOUD_RESOURCE"
    IDENTITY = "IDENTITY"
    SECRET_REFERENCE = "SECRET_REFERENCE"


class SecurityAssetCriticality(str, Enum):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class SecurityAssetExposure(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    RESTRICTED = "RESTRICTED"
    ISOLATED = "ISOLATED"


class SecurityAssetStatus(str, Enum):
    ACTIVE = "ACTIVE"
    DEGRADED = "DEGRADED"
    DEPRECATED = "DEPRECATED"
    INACTIVE = "INACTIVE"


class SecurityAsset(BaseModel):
    asset_id: str = Field(default_factory=lambda: f"asset_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    asset_type: SecurityAssetType
    criticality: SecurityAssetCriticality = SecurityAssetCriticality.HIGH
    exposure: SecurityAssetExposure = SecurityAssetExposure.INTERNAL
    status: SecurityAssetStatus = SecurityAssetStatus.ACTIVE
    architecture_node_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class SecurityAssetManager:
    """Manages enterprise security assets without exposing sensitive secrets."""

    def __init__(self, architecture_manager: Optional[ArchitecturePlatformManager] = None) -> None:
        self.architecture_manager = architecture_manager or ArchitecturePlatformManager()
        self.sanitizer = SensitiveDataSanitizer()
        self._assets: Dict[str, SecurityAsset] = {}

    def register_asset(
        self,
        tenant_id: str,
        name: str,
        asset_type: SecurityAssetType,
        criticality: SecurityAssetCriticality = SecurityAssetCriticality.HIGH,
        exposure: SecurityAssetExposure = SecurityAssetExposure.INTERNAL,
        architecture_node_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> SecurityAsset:
        sanitized_meta = self.sanitizer.sanitize_copy(metadata or {})
        asset = SecurityAsset(
            tenant_id=tenant_id,
            name=name,
            asset_type=asset_type,
            criticality=criticality,
            exposure=exposure,
            architecture_node_id=architecture_node_id,
            metadata=sanitized_meta,
        )
        self._assets[asset.asset_id] = asset
        return asset

    def get_asset(self, asset_id: str, tenant_id: str) -> SecurityAsset:
        asset = self._assets.get(asset_id)
        if not asset:
            raise SecurityIntelligenceException(f"Security asset '{asset_id}' not found.", code="ASSET_NOT_FOUND")
        if tenant_id != "global" and asset.tenant_id != "global" and tenant_id != asset.tenant_id:
            raise CrossTenantSecurityAccessException(tenant_id, asset.tenant_id)
        return asset

    def list_assets(self, tenant_id: str) -> List[SecurityAsset]:
        return [a for a in self._assets.values() if a.tenant_id == tenant_id]
