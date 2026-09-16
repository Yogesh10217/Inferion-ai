from __future__ import annotations

import hashlib
import json
from typing import Any, Dict

from app.deployment.models import ConfigurationFingerprint, EnvironmentConfig

SENSITIVE_KEYWORDS = {
    "secret", "password", "key", "token", "auth", "credential",
    "private", "cert", "dsn", "connection", "jwt", "api_key"
}


class ConfigurationFingerprintEngine:
    """Generates deterministic, sanitized SHA-256 configuration fingerprints without secret leakage."""

    @staticmethod
    def is_sensitive_key(key: str) -> bool:
        lower_key = key.lower()
        return any(kw in lower_key for kw in SENSITIVE_KEYWORDS)

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for key, value in sorted(data.items()):
            if cls.is_sensitive_key(key):
                sanitized[key] = {"configured": bool(value)}
            elif isinstance(value, dict):
                sanitized[key] = cls.sanitize_dict(value)
            elif isinstance(value, list):
                sanitized[key] = [cls.sanitize_dict(item) if isinstance(item, dict) else item for item in value]
            else:
                sanitized[key] = str(value)
        return sanitized

    @classmethod
    def generate_fingerprint(cls, config: EnvironmentConfig) -> ConfigurationFingerprint:
        raw_map = {
            "environment": config.environment.value,
            "application_name": config.application_name,
            "application_version": config.application_version,
            "deployment_version": config.deployment_version,
            "region": config.region,
            "debug_enabled": config.debug_enabled,
            "cache_enabled": config.cache_enabled,
            "messaging_enabled": config.messaging_enabled,
            "observability_enabled": config.observability_enabled,
            "log_level": config.log_level,
        }

        sanitized_map = cls.sanitize_dict(raw_map)
        canonical_json = json.dumps(sanitized_map, sort_keys=True)
        fingerprint_hash = hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

        return ConfigurationFingerprint(
            fingerprint_hash=fingerprint_hash,
            sanitized_keys=list(sanitized_map.keys()),
            environment=config.environment.value,
            deployment_version=config.deployment_version,
        )
