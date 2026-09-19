"""API Key Lifecycle Manager with Hashed Storage & Governance."""

import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.security.exceptions import InvalidAPIKeyError

logger = logging.getLogger(__name__)


class APIKeyPolicy(BaseModel):
    """Policy rules attached to an API key."""

    scopes: List[str] = Field(default_factory=lambda: ["read", "write"])
    permissions: List[str] = Field(default_factory=list)
    allowed_ips: List[str] = Field(default_factory=list)
    allowed_endpoints: List[str] = Field(default_factory=list)
    allowed_models: List[str] = Field(default_factory=list)
    rate_limit_requests_per_min: Optional[int] = None
    rate_limit_tokens_per_min: Optional[int] = None


class APIKey(BaseModel):
    """API Key domain metadata (never stores raw key string)."""

    id: str
    name: str
    key_prefix: str
    hashed_key: str
    tenant_id: str = "global"
    organization_id: Optional[str] = None
    workspace_id: Optional[str] = None
    user_id: Optional[str] = None
    policy: APIKeyPolicy = Field(default_factory=APIKeyPolicy)
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None
    usage_count: int = 0


class APIKeyManager:
    """Manages secure generation, hashed storage, rotation, and revocation of API keys."""

    def __init__(self) -> None:
        self._keys_store: Dict[str, APIKey] = {}  # key_id -> APIKey
        self._hash_index: Dict[str, str] = {}  # hashed_key -> key_id

    @staticmethod
    def hash_key(raw_key: str) -> str:
        """Hash raw key string using SHA-256."""
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def generate_api_key(
        self,
        name: str,
        tenant_id: str = "global",
        organization_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        user_id: Optional[str] = None,
        policy: Optional[APIKeyPolicy] = None,
        expires_in_days: Optional[int] = None,
        prefix: str = "sk-live-",
    ) -> Dict[str, Any]:
        """Generate a new API key. Returns raw key ONLY ONCE."""
        random_bytes = secrets.token_urlsafe(32)
        raw_key = f"{prefix}{random_bytes}"
        key_id = f"key_{secrets.token_hex(8)}"
        hashed = self.hash_key(raw_key)

        exp_dt = datetime.now(timezone.utc) + timedelta(days=expires_in_days) if expires_in_days else None

        key_obj = APIKey(
            id=key_id,
            name=name,
            key_prefix=prefix,
            hashed_key=hashed,
            tenant_id=tenant_id,
            organization_id=organization_id,
            workspace_id=workspace_id,
            user_id=user_id,
            policy=policy or APIKeyPolicy(),
            expires_at=exp_dt,
        )

        self._keys_store[key_id] = key_obj
        self._hash_index[hashed] = key_id

        logger.info(f"Generated new API Key '{name}' (ID: {key_id}, Prefix: {prefix})")
        return {
            "key_id": key_id,
            "name": name,
            "raw_key": raw_key,  # Returned only upon creation!
            "key_prefix": prefix,
            "created_at": key_obj.created_at.isoformat(),
            "expires_at": exp_dt.isoformat() if exp_dt else None,
        }

    def verify_api_key(self, raw_key: str) -> APIKey:
        """Verify raw API key string against stored hashes."""
        if not raw_key:
            raise InvalidAPIKeyError("Raw key is empty")

        hashed = self.hash_key(raw_key)
        key_id = self._hash_index.get(hashed)
        if not key_id or key_id not in self._keys_store:
            raise InvalidAPIKeyError("Invalid API key")

        key_obj = self._keys_store[key_id]
        if not key_obj.is_active or key_obj.revoked_at is not None:
            raise InvalidAPIKeyError("API key is revoked or inactive")

        if key_obj.expires_at and datetime.now(timezone.utc) > key_obj.expires_at:
            raise InvalidAPIKeyError("API key has expired")

        # Record usage
        key_obj.usage_count += 1
        key_obj.last_used_at = datetime.now(timezone.utc)
        return key_obj

    def revoke_api_key(self, key_id: str) -> APIKey:
        """Revoke an API key by ID."""
        if key_id not in self._keys_store:
            raise InvalidAPIKeyError(f"API key ID '{key_id}' not found")

        key_obj = self._keys_store[key_id]
        key_obj.is_active = False
        key_obj.revoked_at = datetime.now(timezone.utc)
        logger.info(f"Revoked API key '{key_id}'")
        return key_obj

    def rotate_api_key(self, key_id: str, expires_in_days: Optional[int] = None) -> Dict[str, Any]:
        """Rotate an existing API key, creating a new key with identical policy while revoking the old one."""
        old_key = self.revoke_api_key(key_id)
        new_result = self.generate_api_key(
            name=f"{old_key.name} (Rotated)",
            tenant_id=old_key.tenant_id,
            organization_id=old_key.organization_id,
            workspace_id=old_key.workspace_id,
            user_id=old_key.user_id,
            policy=old_key.policy,
            expires_in_days=expires_in_days,
            prefix=old_key.key_prefix,
        )
        logger.info(f"Rotated API key '{key_id}' -> new key '{new_result['key_id']}'")
        return new_result

    def list_api_keys(self, tenant_id: str = "global", organization_id: Optional[str] = None) -> List[APIKey]:
        """List API key metadata without revealing secret hashes."""
        res = []
        for k in self._keys_store.values():
            if tenant_id in (k.tenant_id, "global") and (
                organization_id is None or k.organization_id == organization_id
            ):
                res.append(k)
        return res
