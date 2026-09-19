"""Internal Integration Marketplace & Catalog Subsystem."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class MarketplaceListing(BaseModel):
    listing_id: str = Field(default_factory=lambda: f"mkt_{uuid.uuid4().hex[:10]}")
    name: str
    description: str
    category: str = "SAAS"
    publisher: str = "internal"
    version: str = "1.0.0"
    created_at: datetime = Field(default_factory=_now)


class InstallationRecord(BaseModel):
    installation_id: str = Field(default_factory=lambda: f"inst_{uuid.uuid4().hex[:10]}")
    listing_id: str
    tenant_id: str = "global"
    installed_at: datetime = Field(default_factory=_now)


class IntegrationMarketplace:
    """Manages internal integration listings and tenant installations."""

    def __init__(self) -> None:
        self._listings: Dict[str, MarketplaceListing] = {}
        self._installations: Dict[str, InstallationRecord] = {}

    def create_listing(self, name: str, description: str, category: str = "SAAS") -> MarketplaceListing:
        listing = MarketplaceListing(name=name, description=description, category=category)
        self._listings[listing.listing_id] = listing
        logger.info(f"[MARKETPLACE] Created integration listing '{listing.listing_id}' ('{name}')")
        return listing

    def install_integration(self, listing_id: str, tenant_id: str = "global") -> InstallationRecord:
        inst = InstallationRecord(listing_id=listing_id, tenant_id=tenant_id)
        self._installations[inst.installation_id] = inst
        logger.info(
            f"[MARKETPLACE] Installed listing '{listing_id}' for tenant '{tenant_id}' -> Installation '{inst.installation_id}'"
        )
        return inst
