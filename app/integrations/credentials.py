"""Secure Credential Broker & SecretManager Integration."""

import logging
from typing import Optional

from pydantic import BaseModel

from app.security.secrets import SecretManager

logger = logging.getLogger(__name__)


class CredentialReference(BaseModel):
    credential_id: str
    secret_id: str
    tenant_id: str = "global"
    auth_type: str = "OAUTH2"


class CredentialBroker:
    """Brokers secret IDs via SecretManager without returning plaintext secret values."""

    def __init__(self, secret_manager: Optional[SecretManager] = None) -> None:
        self.secret_manager = secret_manager or SecretManager()

    def store_credential(self, secret_name: str, secret_value: str, tenant_id: str = "global") -> CredentialReference:
        self.secret_manager.set_secret(secret_name, secret_value)
        ref = CredentialReference(
            credential_id=f"cred_{secret_name}",
            secret_id=secret_name,
            tenant_id=tenant_id,
        )
        logger.info(f"[CREDENTIAL BROKER] Stored credential reference '{ref.credential_id}' for tenant '{tenant_id}'")
        return ref
