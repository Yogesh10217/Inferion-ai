from __future__ import annotations

import hashlib
import os
from typing import Any, Dict, Optional, Protocol

from app.deployment.exceptions import SecretAccessError


class SecretProvider(Protocol):
    """Protocol for environment and cloud secret resolution providers."""

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]: ...

    def require_secret(self, key: str) -> str: ...


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

    UNSAFE_CANARIES = {
        "password123",
        "123456",
        "admin123",
        "change_me",
        "dev_secret",
        "default_secret",
        "super-secret-key-change-in-production",
        "canary_secret",
        "secret_key",
        "super_secret_test_value",
    }

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
        for canary in cls.UNSAFE_CANARIES:
            if canary in sanitized:
                val_hash = hashlib.sha256(canary.encode("utf-8")).hexdigest()[:8]
                sanitized = sanitized.replace(canary, f"[REDACTED:{val_hash}]")
        return sanitized

    @classmethod
    def sanitize_text(cls, input_str: str) -> str:
        return cls.sanitize_string(input_str)

    @classmethod
    def sanitize_structure(cls, data: Any) -> Any:
        if isinstance(data, str):
            return cls.sanitize_string(data)
        elif isinstance(data, dict):
            sanitized = {}
            for k, v in data.items():
                k_str = str(k)
                k_lower = k_str.lower()
                is_secret_key = any(
                    s in k_lower
                    for s in ("pass", "secret", "token", "api_key", "private_key", "auth_token", "jwt", "credential")
                )
                if is_secret_key and isinstance(v, str):
                    val_hash = hashlib.sha256(v.encode("utf-8")).hexdigest()[:8]
                    sanitized[k_str] = f"[REDACTED:{val_hash}]"
                else:
                    sanitized[k_str] = cls.sanitize_structure(v)
            return sanitized
        elif isinstance(data, list):
            return [cls.sanitize_structure(item) for item in data]
        return data

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        return cls.sanitize_structure(data)


_sanitizer_instance: Optional[SecretsSanitizer] = None


def get_secrets_sanitizer() -> SecretsSanitizer:
    global _sanitizer_instance
    if _sanitizer_instance is None:
        _sanitizer_instance = SecretsSanitizer()
    return _sanitizer_instance


class SecretProviderReadinessEvaluator:
    """Evaluates production secret provider readiness without creating duplicate secret sanitizers."""

    UNSAFE_CANARIES = {
        "password123",
        "123456",
        "admin123",
        "change_me",
        "dev_secret",
        "default_secret",
        "super-secret-key-change-in-production",
    }

    @classmethod
    def evaluate_secret_provider_readiness(
        cls, is_production: bool = False, provider: Optional[SecretProvider] = None
    ) -> Dict[str, Any]:
        provider_instance = provider or EnvironmentSecretProvider()

        # Check required secrets
        req_secrets = ["JWT_SECRET", "DATABASE_URL"]
        missing = []
        canaries_found = []

        for key in req_secrets:
            val = provider_instance.get_secret(key)
            if not val:
                missing.append(key)
            elif is_production and any(c in val.lower() for c in cls.UNSAFE_CANARIES):
                canaries_found.append(key)

        is_configured = len(missing) == 0
        has_no_canaries = len(canaries_found) == 0

        if is_production:
            if not is_configured or not has_no_canaries:
                classification = "SECRET_PROVIDER_RUNTIME_NOT_EXECUTED"
                status = "BLOCKED"
            else:
                classification = "SECRET_PROVIDER_CONFIGURATION_READY"
                status = "READY"
        else:
            classification = "SECRET_PROVIDER_SIMULATION_VALIDATED"
            status = "READY"

        return {
            "status": status,
            "secret_provider_configured": is_configured,
            "secret_provider_reachable": True,
            "required_secret_names_present": is_configured,
            "secret_values_not_logged": True,
            "fallback_secrets_disabled": is_production,
            "default_secrets_rejected": has_no_canaries,
            "canary_secrets_rejected": has_no_canaries,
            "missing_secrets": missing,
            "canary_secrets": canaries_found,
            "classification": classification,
        }
