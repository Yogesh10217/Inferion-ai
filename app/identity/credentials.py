"""API Key & Credential Governance and Rotation Engine."""

from datetime import datetime, timezone, timedelta
from enum import Enum
import uuid
import logging
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field

from app.security.api_keys import APIKeyManager
from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


def _now() -> datetime:
    return datetime.now(timezone.utc)


class CredentialType(str, Enum):
    API_KEY = "API_KEY"
    SERVICE_TOKEN = "SERVICE_TOKEN"
    CLIENT_SECRET = "CLIENT_SECRET"
    CERTIFICATE = "CERTIFICATE"
    SIGNING_KEY = "SIGNING_KEY"
    WEBHOOK_SECRET = "WEBHOOK_SECRET"


class CredentialStatus(str, Enum):
    ACTIVE = "ACTIVE"
    EXPIRED = "EXPIRED"
    ROTATED = "ROTATED"
    REVOKED = "REVOKED"


class Credential(BaseModel):
    credential_id: str = Field(default_factory=lambda: f"cred_{uuid.uuid4().hex[:10]}")
    name: str
    identity_id: str
    tenant_id: str = "global"
    credential_type: CredentialType = CredentialType.API_KEY
    status: CredentialStatus = CredentialStatus.ACTIVE

    secret_key_ref: str = Field(default_factory=lambda: f"sec_ref_{uuid.uuid4().hex[:10]}")
    scopes: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=_now)
    expires_at: Optional[datetime] = None
    last_used_at: Optional[datetime] = None


class CredentialManager:
    """Manages credential governance, scoped permissions, rotation, and revocation."""

    def __init__(
        self,
        api_key_manager: Optional[APIKeyManager] = None,
        secret_manager: Optional[SecretManager] = None,
    ) -> None:
        self.api_key_manager = api_key_manager or APIKeyManager()
        self.secret_manager = secret_manager or SecretManager()
        self._credentials: Dict[str, Credential] = {}

    def create_credential(
        self,
        name: str,
        identity_id: str,
        credential_type: CredentialType = CredentialType.API_KEY,
        tenant_id: str = "global",
        scopes: Optional[List[str]] = None,
        expires_days: int = 90,
    ) -> Credential:
        now = _now()
        cred = Credential(
            name=name,
            identity_id=identity_id,
            tenant_id=tenant_id,
            credential_type=credential_type,
            scopes=scopes or ["read"],
            expires_at=now + timedelta(days=expires_days),
        )
        self._credentials[cred.credential_id] = cred
        logger.info(f"[CREDENTIAL MANAGER] Created credential '{cred.credential_id}' ({name}) for '{identity_id}' (Tenant: {tenant_id})")
        return cred

    def rotate_credential(self, credential_id: str) -> Credential:
        old_cred = self.get_credential(credential_id)
        old_cred.status = CredentialStatus.ROTATED

        # Create new rotated credential
        new_cred = self.create_credential(
            name=f"{old_cred.name}_rotated",
            identity_id=old_cred.identity_id,
            credential_type=old_cred.credential_type,
            tenant_id=old_cred.tenant_id,
            scopes=old_cred.scopes,
        )
        logger.info(f"[CREDENTIAL MANAGER] Rotated credential '{credential_id}' -> New Credential '{new_cred.credential_id}'")
        return new_cred

    def revoke_credential(self, credential_id: str, reason: str = "Revoked by policy") -> Credential:
        cred = self.get_credential(credential_id)
        cred.status = CredentialStatus.REVOKED
        logger.warning(f"[CREDENTIAL MANAGER] Revoked credential '{credential_id}': {reason}")
        return cred

    def get_credential(self, credential_id: str) -> Credential:
        cred = self._credentials.get(credential_id)
        if not cred:
            raise KeyError(f"Credential '{credential_id}' not found")
        return cred
