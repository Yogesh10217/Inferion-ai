from __future__ import annotations

import os
from typing import Optional, Protocol

from app.deployment.exceptions import SecretAccessError


class SecretProvider(Protocol):
    """Protocol for environment and cloud secret resolution providers."""

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        ...

    def require_secret(self, key: str) -> str:
        ...


class EnvironmentSecretProvider:
    """Environment variable-backed secret provider."""

    def __init__(self, prefix: str = "") -> None:
        self.prefix = prefix

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        lookup_key = f"{self.prefix}{key}" if self.prefix else key
        val = os.getenv(lookup_key) or os.getenv(key)
        return val if val is not None else default

    def require_secret(self, key: str) -> str:
        secret = self.get_secret(key)
        if not secret:
            raise SecretAccessError(f"Required secret reference '{key}' is missing from environment secrets provider")
        return secret


class VaultSecretProvider:
    """Vault secret provider reference implementation (advisory contract)."""

    def __init__(self, vault_url: str = "http://localhost:8200") -> None:
        self.vault_url = vault_url

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        # Clean protocol abstraction fallback to environment
        return os.getenv(key, default)

    def require_secret(self, key: str) -> str:
        val = self.get_secret(key)
        if not val:
            raise SecretAccessError(f"Required Vault secret key '{key}' is missing")
        return val
