"""Model Lifecycle Management Subsystem."""

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.mlops.registry import AIAssetRegistry, AIAssetType

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class ModelProvider(str, Enum):
    LOCAL = "LOCAL"
    OPENAI = "OPENAI"
    ANTHROPIC = "ANTHROPIC"
    GOOGLE = "GOOGLE"
    AZURE = "AZURE"
    BEDROCK = "BEDROCK"
    CUSTOM = "CUSTOM"


class ModelMetadata(BaseModel):
    """Detailed model capability and performance metadata."""

    model_name: str
    model_provider: ModelProvider
    model_version: str
    context_window: int = 128000
    capabilities: List[str] = Field(default_factory=lambda: ["chat", "tool_calling", "json_mode"])
    pricing_per_1k_tokens: float = 0.0015
    latency_profile_ms: float = 120.0
    quality_score: float = 95.0
    safety_score: float = 98.0


class ModelLifecycleManager:
    """Manages model asset registration, capability validation, provider configuration, and lifecycle tracking."""

    def __init__(self, registry: Optional[AIAssetRegistry] = None) -> None:
        self.registry = registry or AIAssetRegistry()

    def register_model(
        self,
        name: str,
        provider: ModelProvider,
        version_str: str,
        context_window: int = 128000,
        tenant_id: str = "global",
        capabilities: Optional[List[str]] = None,
        pricing: float = 0.0015,
        latency_ms: float = 120.0,
    ) -> Dict[str, Any]:
        meta = ModelMetadata(
            model_name=name,
            model_provider=provider,
            model_version=version_str,
            context_window=context_window,
            capabilities=capabilities or ["chat", "tool_calling", "json_mode"],
            pricing_per_1k_tokens=pricing,
            latency_profile_ms=latency_ms,
        )

        asset = self.registry.register_asset(
            name=name,
            asset_type=AIAssetType.MODEL,
            tenant_id=tenant_id,
            description=f"{provider.value} Model: {name} v{version_str}",
            initial_configuration=meta.model_dump(),
        )

        logger.info(f"[MODEL LIFECYCLE] Registered model '{name}' (Provider: {provider.value}, Version: {version_str})")
        return {"asset_id": asset.asset_id, "metadata": meta.model_dump()}

    def validate_capabilities(self, asset_id: str, required_capabilities: List[str]) -> bool:
        asset = self.registry.get_asset(asset_id)
        current_ver = self.registry.get_version(asset_id, asset.current_version)
        caps = current_ver.configuration.get("capabilities", [])

        for req in required_capabilities:
            if req not in caps:
                logger.warning(f"[MODEL LIFECYCLE] Model '{asset.name}' missing capability '{req}'")
                return False
        return True
