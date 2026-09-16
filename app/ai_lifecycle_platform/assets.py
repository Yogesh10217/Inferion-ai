"""Enterprise AI Asset Registry Subsystem (Phase 5.33)."""

import uuid
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.ai_lifecycle_platform.exceptions import AIAssetNotFoundException, CrossTenantLifecycleAccessException


class AIAssetType(str, Enum):
    DATASET = "DATASET"
    MODEL = "MODEL"
    FOUNDATION_MODEL = "FOUNDATION_MODEL"
    FINE_TUNED_MODEL = "FINE_TUNED_MODEL"
    PROMPT = "PROMPT"
    AGENT = "AGENT"
    TOOL = "TOOL"
    KNOWLEDGE_BASE = "KNOWLEDGE_BASE"
    EVALUATION_SUITE = "EVALUATION_SUITE"
    MODEL_PACKAGE = "MODEL_PACKAGE"


class AIAssetStatus(str, Enum):
    REGISTERED = "REGISTERED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    RETIRED = "RETIRED"


class AIAsset(BaseModel):
    asset_id: str = Field(default_factory=lambda: f"aiast_{uuid.uuid4().hex[:12]}")
    tenant_id: str
    name: str
    description: str = ""
    asset_type: AIAssetType = AIAssetType.MODEL
    owner_reference: str = "system"
    version: str = "1.0.0"
    status: AIAssetStatus = AIAssetStatus.REGISTERED
    lifecycle_stage: str = "REGISTERED"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    lineage_references: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AIAssetManager:
    """Enterprise AI Asset Registry Manager."""

    def __init__(self) -> None:
        self._assets: Dict[str, AIAsset] = {}

    def register_asset(
        self,
        tenant_id: str,
        name: str,
        asset_type: AIAssetType = AIAssetType.MODEL,
        description: str = "",
        owner_reference: str = "system",
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AIAsset:
        asset = AIAsset(
            tenant_id=tenant_id,
            name=name,
            asset_type=asset_type,
            description=description,
            owner_reference=owner_reference,
            metadata=metadata or {},
        )
        self._assets[asset.asset_id] = asset
        return asset

    def get_asset(self, asset_id: str, tenant_id: str) -> AIAsset:
        asset = self._assets.get(asset_id)
        if not asset:
            raise AIAssetNotFoundException(asset_id)
        if tenant_id != "global" and asset.tenant_id != "global" and tenant_id != asset.tenant_id:
            raise CrossTenantLifecycleAccessException(tenant_id, asset.tenant_id)
        return asset

    def list_assets(self, tenant_id: str) -> List[AIAsset]:
        return [a for a in self._assets.values() if a.tenant_id == tenant_id]
