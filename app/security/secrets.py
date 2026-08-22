"""Secret Management Platform Abstraction & Automatic Redaction."""

import os
import re
import logging
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Set
from datetime import datetime, timezone

from app.security.exceptions import SecretAccessDeniedError

logger = logging.getLogger(__name__)

# Patterns for sensitive tokens, keys, credentials
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|bearer|jwt|access[_-]?token)=['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?"),
    re.compile(r"sk-[a-zA-Z0-9]{20,}"),
    re.compile(r"eyJ[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9_\-\.]+\.[a-zA-Z0-9_\-\.]+"),
]


class SecretProvider(ABC):
    """Abstract interface for secret backends (Environment, HashiCorp Vault, AWS Secrets Manager)."""

    @abstractmethod
    def get_secret(self, key: str) -> Optional[str]:
        pass

    @abstractmethod
    def set_secret(self, key: str, value: str) -> None:
        pass

    @abstractmethod
    def delete_secret(self, key: str) -> bool:
        pass


class EnvironmentSecretProvider(SecretProvider):
    """Secret provider retrieving secrets from environment variables."""

    def __init__(self) -> None:
        self._local_overrides: Dict[str, str] = {}

    def get_secret(self, key: str) -> Optional[str]:
        return self._local_overrides.get(key) or os.environ.get(key)

    def set_secret(self, key: str, value: str) -> None:
        self._local_overrides[key] = value

    def delete_secret(self, key: str) -> bool:
        if key in self._local_overrides:
            del self._local_overrides[key]
            return True
        return False


class SecretManager:
    """Enterprise Secret Manager with automatic redaction and multi-backend support."""

    def __init__(self, primary_provider: Optional[SecretProvider] = None) -> None:
        self.provider = primary_provider or EnvironmentSecretProvider()
        self._known_secrets: Set[str] = set()

    def register_secret_value(self, secret_value: str) -> None:
        """Register a sensitive value to be automatically redacted."""
        if secret_value and len(secret_value) > 4:
            self._known_secrets.add(secret_value)

    def get_secret(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Retrieve a secret from the underlying provider."""
        val = self.provider.get_secret(key) or default
        if val:
            self.register_secret_value(val)
        return val

    def set_secret(self, key: str, value: str) -> None:
        """Persist or update a secret."""
        self.provider.set_secret(key, value)
        self.register_secret_value(value)
        logger.info(f"Updated secret key '{key}'")

    def delete_secret(self, key: str) -> bool:
        """Delete a secret."""
        return self.provider.delete_secret(key)

    def rotate_secret(self, key: str, new_value: str) -> None:
        """Rotate a secret value."""
        self.set_secret(key, new_value)
        logger.info(f"Rotated secret key '{key}'")

    def sanitize_text(self, text: str) -> str:
        """Redact registered secret values and regex secret patterns from text."""
        if not text:
            return text

        result = str(text)

        # 1. Known secret strings
        for secret in list(self._known_secrets):
            if secret in result:
                result = result.replace(secret, "[REDACTED_SECRET]")

        # 2. Pattern matching
        for pattern in SECRET_PATTERNS:
            try:
                result = pattern.sub("[REDACTED_SECRET]", result)
            except Exception:
                pass

        return result

