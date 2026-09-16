"""Misconfiguration Detection Engine."""

import uuid
from datetime import datetime, timezone
from typing import List

from pydantic import BaseModel, Field

from app.security_assurance.asset_inventory import SecurityAssetInventory
from app.security_assurance.assets import SecurityAssetType


class SecurityMisconfiguration(BaseModel):
    misconfig_id: str = Field(default_factory=lambda: f"misconfig-{uuid.uuid4().hex[:8]}")
    tenant_id: str
    asset_id: str
    category: str  # PERMISSIONS, ENCRYPTION, NETWORK, AUTH
    title: str
    severity: str  # LOW, MEDIUM, HIGH, CRITICAL
    recommendation: str
    detected_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class MisconfigurationDetector:
    """Detects security misconfigurations across assets."""

    def __init__(self, asset_inventory: SecurityAssetInventory) -> None:
        self.asset_inventory = asset_inventory

    def scan_misconfigurations(self, tenant_id: str) -> List[SecurityMisconfiguration]:
        assets = self.asset_inventory.list_assets(tenant_id)
        misconfigs = []
        for asset in assets:
            if asset.asset_type == SecurityAssetType.API_ENDPOINT and asset.location == "external":
                misconfigs.append(
                    SecurityMisconfiguration(
                        tenant_id=tenant_id,
                        asset_id=asset.asset_id,
                        category="NETWORK",
                        title="Unrestricted external API endpoint without rate limiting header",
                        severity="MEDIUM",
                        recommendation="Enforce rate limiting and API key authentication.",
                    )
                )
            if asset.asset_type == SecurityAssetType.AI_MODEL and asset.metadata.get("logging_level") == "DEBUG":
                misconfigs.append(
                    SecurityMisconfiguration(
                        tenant_id=tenant_id,
                        asset_id=asset.asset_id,
                        category="LOGGING",
                        title="Model DEBUG logging active in production environment",
                        severity="HIGH",
                        recommendation="Set model log level to INFO or WARN to prevent prompt leakage.",
                    )
                )
        return misconfigs
