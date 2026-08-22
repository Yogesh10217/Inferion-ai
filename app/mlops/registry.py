"""Unified AI Asset Registry & Versioning Subsystem."""

from datetime import datetime, timezone
from enum import Enum
import uuid
import hashlib
import json
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.mlops.exceptions import AssetNotFoundException, VersionNotFoundException, GovernanceViolationException

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class AIAssetType(str, Enum):
    MODEL = "MODEL"
    MODEL_CONFIGURATION = "MODEL_CONFIGURATION"
    PROMPT = "PROMPT"
    PROMPT_TEMPLATE = "PROMPT_TEMPLATE"
    AGENT = "AGENT"
    AGENT_TEAM = "AGENT_TEAM"
    WORKFLOW = "WORKFLOW"
    WORKFLOW_TEMPLATE = "WORKFLOW_TEMPLATE"
    TOOL_CONFIGURATION = "TOOL_CONFIGURATION"
    MCP_PACKAGE = "MCP_PACKAGE"
    KNOWLEDGE_CONFIGURATION = "KNOWLEDGE_CONFIGURATION"
    REASONING_STRATEGY = "REASONING_STRATEGY"
    PLANNING_STRATEGY = "PLANNING_STRATEGY"
    EXTENSION = "EXTENSION"


class AIAssetStatus(str, Enum):
    DRAFT = "DRAFT"
    DEVELOPMENT = "DEVELOPMENT"
    TESTING = "TESTING"
    VALIDATED = "VALIDATED"
    APPROVED = "APPROVED"
    STAGED = "STAGED"
    PRODUCTION = "PRODUCTION"
    DEPRECATED = "DEPRECATED"
    ARCHIVED = "ARCHIVED"
    FAILED = "FAILED"
    ROLLED_BACK = "ROLLED_BACK"


class AIAssetVersion(BaseModel):
    """Immutable version snapshot for an AI asset."""

    version_id: str = Field(default_factory=lambda: f"ver_{uuid.uuid4().hex[:10]}")
    version_number: str  # SemVer e.g. "1.0.0"
    asset_id: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None

    creator: str = "system"
    configuration: Dict[str, Any] = Field(default_factory=dict)
    configuration_hash: str = ""
    dependencies: Dict[str, str] = Field(default_factory=dict)  # asset_id -> required_version
    parent_version: Optional[str] = None
    changelog: str = ""

    status: AIAssetStatus = AIAssetStatus.DRAFT
    approval_status: str = "NOT_REQUESTED"
    created_at: datetime = Field(default_factory=_now)
    is_immutable: bool = False

    def model_post_init(self, __context: Any) -> None:
        if not self.configuration_hash:
            config_str = json.dumps(self.configuration, sort_keys=True)
            self.configuration_hash = hashlib.sha256(config_str.encode("utf-8")).hexdigest()


class AIAsset(BaseModel):
    """Top-level AI Asset container."""

    asset_id: str = Field(default_factory=lambda: f"asset_{uuid.uuid4().hex[:10]}")
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None

    name: str
    asset_type: AIAssetType
    description: str = ""

    current_version: str = "1.0.0"
    status: AIAssetStatus = AIAssetStatus.DRAFT
    versions: List[AIAssetVersion] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=_now)
    updated_at: datetime = Field(default_factory=_now)


class AIAssetRegistry:
    """Central multi-tenant registry for AI Assets, versions, dependency tracking, and immutable promotions."""

    def __init__(self) -> None:
        self._assets: Dict[str, AIAsset] = {}

    def register_asset(
        self,
        name: str,
        asset_type: AIAssetType,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        description: str = "",
        initial_configuration: Optional[Dict[str, Any]] = None,
    ) -> AIAsset:
        asset = AIAsset(
            name=name,
            asset_type=asset_type,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            description=description,
        )

        initial_ver = AIAssetVersion(
            version_number="1.0.0",
            asset_id=asset.asset_id,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            configuration=initial_configuration or {},
            status=AIAssetStatus.DEVELOPMENT,
        )
        asset.versions.append(initial_ver)
        self._assets[asset.asset_id] = asset

        logger.info(f"[AI ASSET REGISTRY] Registered asset '{asset.name}' (ID: {asset.asset_id}, Type: {asset.asset_type.value}, Tenant: {tenant_id})")
        return asset

    def create_version(
        self,
        asset_id: str,
        version_number: str,
        configuration: Dict[str, Any],
        creator: str = "system",
        changelog: str = "",
        dependencies: Optional[Dict[str, str]] = None,
    ) -> AIAssetVersion:
        asset = self.get_asset(asset_id)
        parent_ver = asset.versions[-1].version_number if asset.versions else None

        ver = AIAssetVersion(
            version_number=version_number,
            asset_id=asset.asset_id,
            tenant_id=asset.tenant_id,
            organization_id=asset.organization_id,
            workspace_id=asset.workspace_id,
            creator=creator,
            configuration=configuration,
            changelog=changelog,
            dependencies=dependencies or {},
            parent_version=parent_ver,
            status=AIAssetStatus.DEVELOPMENT,
        )
        asset.versions.append(ver)
        asset.current_version = version_number
        asset.updated_at = _now()

        logger.info(f"[AI ASSET REGISTRY] Created version '{version_number}' for asset '{asset.name}' (Hash: {ver.configuration_hash[:8]}...)")
        return ver

    def get_asset(self, asset_id: str) -> AIAsset:
        asset = self._assets.get(asset_id)
        if not asset:
            raise AssetNotFoundException(asset_id)
        return asset

    def get_version(self, asset_id: str, version_number: str) -> AIAssetVersion:
        asset = self.get_asset(asset_id)
        for v in asset.versions:
            if v.version_number == version_number:
                return v
        raise VersionNotFoundException(asset_id, version_number)

    def list_assets(
        self,
        tenant_id: Optional[str] = None,
        asset_type: Optional[AIAssetType] = None,
        status: Optional[AIAssetStatus] = None,
    ) -> List[AIAsset]:
        res = list(self._assets.values())
        if tenant_id:
            res = [a for a in res if a.tenant_id == tenant_id]
        if asset_type:
            res = [a for a in res if a.asset_type == asset_type]
        if status:
            res = [a for a in res if a.status == status]
        return res

    def promote_version(self, asset_id: str, version_number: str, target_status: AIAssetStatus) -> AIAssetVersion:
        """Promote version status. Production promotions lock version as immutable."""
        asset = self.get_asset(asset_id)
        ver = self.get_version(asset_id, version_number)

        if ver.is_immutable and target_status == AIAssetStatus.PRODUCTION:
            logger.info(f"[AI ASSET REGISTRY] Version '{version_number}' already immutable production")
            return ver

        ver.status = target_status
        if target_status == AIAssetStatus.PRODUCTION:
            ver.is_immutable = True  # Lock production version as immutable!
            asset.status = AIAssetStatus.PRODUCTION

        logger.info(f"[AI ASSET REGISTRY] Promoted version '{version_number}' of asset '{asset.name}' to '{target_status.value}' (Immutable: {ver.is_immutable})")
        return ver

    def rollback_version(self, asset_id: str, target_version_number: str) -> AIAssetVersion:
        """Rollback current active version to a previously validated target version."""
        asset = self.get_asset(asset_id)
        target_ver = self.get_version(asset_id, target_version_number)

        asset.current_version = target_ver.version_number
        asset.status = target_ver.status
        asset.updated_at = _now()

        logger.info(f"[AI ASSET REGISTRY] Rolled back asset '{asset.name}' to version '{target_ver.version_number}'")
        return target_ver
