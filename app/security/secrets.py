"""Secret Management Platform Abstraction & Automatic Redaction."""

import logging
import os
import re
from abc import ABC, abstractmethod
from typing import Dict, Optional, Set

logger = logging.getLogger(__name__)

# Patterns for sensitive tokens, keys, credentials
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|password|bearer|jwt|access[_-]?token)=['\"]?([a-zA-Z0-9_\-\.]{8,})['\"]?"),
    re.compile(r"sk-[a-zA-Z0-9_\-]{20,}"),
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


class VaultSecretProvider(SecretProvider):
    """HashiCorp Vault Secret Provider (KV v2 REST API)."""

    def __init__(
        self,
        vault_url: Optional[str] = None,
        vault_token: Optional[str] = None,
        mount_point: str = "secret",
    ) -> None:
        self.vault_url = (vault_url or os.environ.get("VAULT_ADDR", "http://127.0.0.1:8200")).rstrip("/")
        self.vault_token = vault_token or os.environ.get("VAULT_TOKEN", "")
        self.mount_point = mount_point
        self._cache: Dict[str, str] = {}

    def get_secret(self, key: str) -> Optional[str]:
        if key in self._cache:
            return self._cache[key]

        if not self.vault_token:
            return os.environ.get(key)

        try:
            import urllib.request
            import json

            req_url = f"{self.vault_url}/v1/{self.mount_point}/data/{key}"
            req = urllib.request.Request(
                req_url, headers={"X-Vault-Token": self.vault_token, "Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=3.0) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                secret_val = data.get("data", {}).get("data", {}).get("value")
                if secret_val:
                    self._cache[key] = secret_val
                    return secret_val
        except Exception as e:
            logger.debug(f"Vault fetch failed for key '{key}': {e}")

        return os.environ.get(key)

    def set_secret(self, key: str, value: str) -> None:
        self._cache[key] = value
        if not self.vault_token:
            os.environ[key] = value
            return

        try:
            import urllib.request
            import json

            req_url = f"{self.vault_url}/v1/{self.mount_point}/data/{key}"
            payload = json.dumps({"data": {"value": value}}).encode("utf-8")
            req = urllib.request.Request(
                req_url,
                data=payload,
                headers={"X-Vault-Token": self.vault_token, "Content-Type": "application/json"},
                method="POST",
            )
            with urllib.request.urlopen(req, timeout=3.0):
                pass
        except Exception as e:
            logger.warning(f"Vault write failed for key '{key}': {e}")
            os.environ[key] = value

    def delete_secret(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
            return True
        return False


class AWSSecretsManagerProvider(SecretProvider):
    """AWS Secrets Manager & KMS Secret Provider."""

    def __init__(self, region_name: str = "us-east-1") -> None:
        self.region_name = os.environ.get("AWS_REGION", region_name)
        self._cache: Dict[str, str] = {}

    def get_secret(self, key: str) -> Optional[str]:
        if key in self._cache:
            return self._cache[key]

        try:
            import boto3

            client = boto3.client("secretsmanager", region_name=self.region_name)
            response = client.get_secret_value(SecretId=key)
            secret_str = response.get("SecretString", "")
            if secret_str:
                self._cache[key] = secret_str
                return secret_str
        except Exception as e:
            logger.debug(f"AWS Secrets Manager fetch failed for key '{key}': {e}")

        return os.environ.get(key)

    def set_secret(self, key: str, value: str) -> None:
        self._cache[key] = value
        try:
            import boto3

            client = boto3.client("secretsmanager", region_name=self.region_name)
            client.put_secret_value(SecretId=key, SecretString=value)
        except Exception as e:
            logger.warning(f"AWS Secrets Manager write failed for key '{key}': {e}")
            os.environ[key] = value

    def delete_secret(self, key: str) -> bool:
        if key in self._cache:
            del self._cache[key]
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
