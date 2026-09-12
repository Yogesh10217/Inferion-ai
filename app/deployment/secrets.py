from __future__ import annotations

import hashlib
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


class SecretsSanitizer:
    """SHA-256 backed string sanitizer masking passwords, keys, and tokens."""

    import re
    SECRET_PATTERN = re.compile(
        r"(password|passwd|secret|jwt_secret|api_key|token|private_key|auth_token)[:=]\s*([^\s,;&'\"]+)",
        re.IGNORECASE,
    )
    URL_CREDS_PATTERN = re.compile(r"://([^:@]+):([^@]+)@", re.IGNORECASE)

    @classmethod
    def sanitize_string(cls, input_str: str) -> str:
        if not input_str:
            return ""
        # Redact URL credentials: postgresql://user:password@host -> postgresql://user:[REDACTED]@host
        sanitized = cls.URL_CREDS_PATTERN.sub(r"://\1:[REDACTED]@", input_str)

        # Redact key-value secrets
        def replace_kv(match):
            key = match.group(1)
            val = match.group(2)
            val_hash = hashlib.sha256(val.encode("utf-8")).hexdigest()[:8]
            return f"{key}=[REDACTED:{val_hash}]"

        sanitized = cls.SECRET_PATTERN.sub(replace_kv, sanitized)
        return sanitized

    @classmethod
    def sanitize_text(cls, input_str: str) -> str:
        return cls.sanitize_string(input_str)

    @classmethod
    def sanitize_structure(cls, data: Any) -> Any:
        if isinstance(data, str):
            return cls.sanitize_string(data)
        elif isinstance(data, dict):
            return {k: cls.sanitize_structure(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.sanitize_structure(item) for item in data]
        return data


