"""Developer API Management integrating Key Generation, Scopes, Quotas, and Analytics."""

import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timezone
import uuid
from pydantic import BaseModel, Field

from app.security.api_keys import APIKeyManager, APIKey
from app.governance.rate_limiter import RateLimiter
from app.governance.quota_manager import QuotaManager


logger = logging.getLogger(__name__)


class DeveloperAPIEndpoint(BaseModel):
    """Registered developer API endpoint."""

    endpoint_id: str = Field(default_factory=lambda: f"ep_{uuid.uuid4().hex[:8]}")
    path: str
    method: str = "GET"
    version: str = "v1"
    required_scopes: List[str] = Field(default_factory=list)
    is_deprecated: bool = False
    sunset_date: Optional[datetime] = None


class DeveloperAPIManager:
    """Manages developer API keys, scope restrictions, endpoint registries, deprecation, and quotas."""

    def __init__(
        self,
        api_key_manager: Optional[APIKeyManager] = None,
        rate_limiter: Optional[RateLimiter] = None,
        quota_manager: Optional[QuotaManager] = None,
    ) -> None:
        self.api_key_manager = api_key_manager or APIKeyManager()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.quota_manager = quota_manager or QuotaManager()
        self._endpoints: Dict[str, DeveloperAPIEndpoint] = {}

    def issue_developer_key(
        self,
        developer_id: str,
        name: str,
        tenant_id: str = "global",
        scopes: Optional[List[str]] = None,
        expires_in_days: Optional[int] = 365,
    ) -> Dict[str, Any]:
        """Issue a cryptographically secure developer API key."""
        raw_key, api_key_obj = self.api_key_manager.create_api_key(
            name=f"dev:{developer_id}:{name}",
            tenant_id=tenant_id,
            scopes=scopes or ["read", "write", "extensions:manage"],
            expires_in_days=expires_in_days,
        )
        logger.info(f"[DEVELOPER API MANAGER] Issued API key '{api_key_obj.key_id}' for dev '{developer_id}'")
        return {
            "key_id": api_key_obj.key_id,
            "raw_key": raw_key,  # Only returned once!
            "prefix": api_key_obj.prefix,
            "scopes": api_key_obj.scopes,
            "expires_at": api_key_obj.expires_at.isoformat() if api_key_obj.expires_at else None,
        }

    def rotate_developer_key(self, key_id: str) -> Dict[str, Any]:
        """Rotate developer key, revoking old key and issuing new one."""
        old_key = self.api_key_manager.get_api_key(key_id)
        if not old_key:
            raise RuntimeError(f"API key '{key_id}' not found")

        self.api_key_manager.revoke_api_key(key_id, reason="Developer key rotation")
        raw_key, new_key = self.api_key_manager.create_api_key(
            name=old_key.name,
            tenant_id=old_key.tenant_id,
            scopes=old_key.scopes,
        )
        logger.info(f"[DEVELOPER API MANAGER] Rotated key '{key_id}' -> '{new_key.key_id}'")
        return {
            "key_id": new_key.key_id,
            "raw_key": raw_key,
            "scopes": new_key.scopes,
        }

    def register_endpoint(
        self,
        path: str,
        method: str = "GET",
        version: str = "v1",
        scopes: Optional[List[str]] = None,
    ) -> DeveloperAPIEndpoint:
        """Register developer API endpoint."""
        ep = DeveloperAPIEndpoint(path=path, method=method, version=version, required_scopes=scopes or [])
        self._endpoints[ep.endpoint_id] = ep
        return ep

    def deprecate_endpoint(self, endpoint_id: str, sunset_date: Optional[datetime] = None) -> DeveloperAPIEndpoint:
        """Deprecate developer API endpoint."""
        ep = self._endpoints.get(endpoint_id)
        if not ep:
            raise RuntimeError(f"Endpoint '{endpoint_id}' not found")
        ep.is_deprecated = True
        ep.sunset_date = sunset_date or datetime.now(timezone.utc)
        return ep
