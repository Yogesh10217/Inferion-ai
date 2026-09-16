"""Security Asset Inventory Management."""

import logging
from typing import Dict, List, Optional

from app.security_assurance.assets import SecurityAsset, SecurityAssetType, SecurityCriticality
from app.security_assurance.exceptions import CrossTenantSecurityAssuranceException, SecurityAssetNotFoundException

logger = logging.getLogger(__name__)


class SecurityAssetInventory:
    """Manages inventory of security-monitored assets across tenants."""

    def __init__(self) -> None:
        self._assets: Dict[str, SecurityAsset] = {}

    def register_asset(
        self,
        tenant_id: str,
        name: str,
        asset_type: SecurityAssetType,
        criticality: SecurityCriticality = SecurityCriticality.MEDIUM,
        location: str = "internal",
        owner: str = "security-team",
        metadata: Optional[Dict] = None,
    ) -> SecurityAsset:
        asset = SecurityAsset(
            tenant_id=tenant_id,
            name=name,
            asset_type=asset_type,
            criticality=criticality,
            location=location,
            owner=owner,
            metadata=metadata or {},
        )
        self._assets[asset.asset_id] = asset
        logger.info(f"[SECURITY ASSET INVENTORY] Registered asset {asset.asset_id} ({name}) for tenant {tenant_id}")
        return asset

    def get_asset(self, tenant_id: str, asset_id: str) -> SecurityAsset:
        asset = self._assets.get(asset_id)
        if not asset:
            raise SecurityAssetNotFoundException(f"Security asset '{asset_id}' not found.")
        if asset.tenant_id != tenant_id:
            raise CrossTenantSecurityAssuranceException("Access denied.")
        return asset

    def list_assets(self, tenant_id: str, asset_type: Optional[SecurityAssetType] = None) -> List[SecurityAsset]:
        results = [a for a in self._assets.values() if a.tenant_id == tenant_id]
        if asset_type:
            results = [a for a in results if a.asset_type == asset_type]
        return results

    def remove_asset(self, tenant_id: str, asset_id: str) -> bool:
        asset = self.get_asset(tenant_id, asset_id)
        del self._assets[asset.asset_id]
        return True
