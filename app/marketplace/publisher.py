"""Publisher entity & reputation management."""

import logging
import uuid
from datetime import datetime, timezone
from typing import Dict, Optional

from pydantic import BaseModel, Field

from app.marketplace.exceptions import PublisherNotFoundException

logger = logging.getLogger(__name__)


class PublisherProfile(BaseModel):
    """Publisher metadata profile."""

    name: str
    email: str
    website: Optional[str] = None
    organization_id: Optional[str] = None


class PublisherVerification(BaseModel):
    """Publisher verification metadata."""

    is_verified: bool = False
    verification_tier: str = "COMMUNITY"  # 'COMMUNITY', 'VERIFIED_DEVELOPER', 'ENTERPRISE_PARTNER'
    verified_at: Optional[datetime] = None


class Publisher(BaseModel):
    """Marketplace publisher identity container."""

    publisher_id: str = Field(default_factory=lambda: f"pub_{uuid.uuid4().hex[:10]}")
    developer_id: str
    tenant_id: str = "global"
    profile: PublisherProfile
    verification: PublisherVerification = Field(default_factory=PublisherVerification)
    reputation_score: float = 100.0
    published_items_count: int = 0
    is_suspended: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PublisherManager:
    """Manages publishers, verification tiers, publishing permissions, and suspension."""

    def __init__(self) -> None:
        self._publishers: Dict[str, Publisher] = {}

    def register_publisher(
        self,
        developer_id: str,
        name: str,
        email: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
    ) -> Publisher:
        """Register a new marketplace publisher."""
        prof = PublisherProfile(name=name, email=email, organization_id=organization_id)
        pub = Publisher(developer_id=developer_id, tenant_id=tenant_id, profile=prof)
        self._publishers[pub.publisher_id] = pub
        logger.info(f"[PUBLISHER MANAGER] Registered publisher '{name}' (ID: {pub.publisher_id})")
        return pub

    def get_publisher(self, publisher_id: str) -> Publisher:
        pub = self._publishers.get(publisher_id)
        if not pub:
            raise PublisherNotFoundException(publisher_id)
        return pub

    def verify_publisher(self, publisher_id: str, tier: str = "VERIFIED_DEVELOPER") -> Publisher:
        pub = self.get_publisher(publisher_id)
        pub.verification.is_verified = True
        pub.verification.verification_tier = tier
        pub.verification.verified_at = datetime.now(timezone.utc)
        logger.info(f"[PUBLISHER MANAGER] Verified publisher '{publisher_id}' tier={tier}")
        return pub
