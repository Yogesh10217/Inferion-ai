"""Data & Asset Exposure Analyzer."""

from typing import Dict, Any, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security_assurance.asset_inventory import SecurityAssetInventory
from app.security_assurance.assets import SecurityAssetType


class ExposureRiskAssessment(BaseModel):
    assessment_id: str = Field(default_factory=lambda: f"exposure-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    public_facing_assets_count: int
    unencrypted_data_assets_count: int
    exposure_level: str  # LOW, MODERATE, SEVERE
    evaluated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ExposureAnalyzer:
    """Analyzes exposure risks for sensitive data and models."""

    def __init__(self, asset_inventory: SecurityAssetInventory) -> None:
        self.asset_inventory = asset_inventory

    def evaluate_exposure(self, tenant_id: str) -> ExposureRiskAssessment:
        assets = self.asset_inventory.list_assets(tenant_id)
        public = [a for a in assets if a.location == "external" or a.location == "public"]
        unencrypted = [a for a in assets if a.metadata.get("encrypted") is False]

        level = "LOW"
        if len(public) > 5 or len(unencrypted) > 0:
            level = "SEVERE" if len(unencrypted) > 2 else "MODERATE"

        return ExposureRiskAssessment(
            tenant_id=tenant_id,
            public_facing_assets_count=len(public),
            unencrypted_data_assets_count=len(unencrypted),
            exposure_level=level,
        )
