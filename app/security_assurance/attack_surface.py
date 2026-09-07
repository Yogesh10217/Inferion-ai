"""Attack Surface Analyzer & Profiles."""

from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security_assurance.asset_inventory import SecurityAssetInventory
from app.security_assurance.assets import SecurityAssetType


class AttackSurfaceProfile(BaseModel):
    profile_id: str = Field(default_factory=lambda: f"asp-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    total_exposed_assets: int
    external_endpoints_count: int
    public_datasets_count: int
    ai_models_count: int
    agents_count: int
    exposure_score: float  # 0.0 (minimal exposure) to 100.0 (high exposure)
    analyzed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class AttackSurfaceAnalyzer:
    """Analyzes overall attack surface exposure for a tenant."""

    def __init__(self, asset_inventory: SecurityAssetInventory) -> None:
        self.asset_inventory = asset_inventory

    def analyze_attack_surface(self, tenant_id: str) -> AttackSurfaceProfile:
        assets = self.asset_inventory.list_assets(tenant_id)
        external = [a for a in assets if a.location == "external" or a.location == "public"]
        external_endpoints = len([a for a in external if a.asset_type == SecurityAssetType.API_ENDPOINT])
        public_datasets = len([a for a in external if a.asset_type == SecurityAssetType.DATASET])
        ai_models = len([a for a in assets if a.asset_type == SecurityAssetType.AI_MODEL])
        agents = len([a for a in assets if a.asset_type == SecurityAssetType.AGENT])

        exposure_score = min(100.0, round((len(external) * 15.0) + (ai_models * 5.0) + (agents * 8.0), 2))

        return AttackSurfaceProfile(
            tenant_id=tenant_id,
            total_exposed_assets=len(external),
            external_endpoints_count=external_endpoints,
            public_datasets_count=public_datasets,
            ai_models_count=ai_models,
            agents_count=agents,
            exposure_score=exposure_score,
        )
