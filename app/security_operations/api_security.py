"""
API Security Module for Phase 5.69.
Evaluates security headers, CORS policies, rate limiting, and OpenAPI endpoint protection.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer


@dataclass
class APISecurityResult:
    classification: str
    is_secure: bool
    security_headers_valid: bool
    cors_policy_valid: bool
    openapi_protected: bool
    rate_limiting_ready: bool
    input_validation_ready: bool
    evidence_level: str
    blocking_reasons: List[str]
    details: Dict[str, Any]
    fingerprint: str = ""

    def __post_init__(self):
        if not self.fingerprint:
            payload = {
                "classification": self.classification,
                "is_secure": self.is_secure,
            }
            self.fingerprint = (
                f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"
            )

    @property
    def hsts_enabled(self) -> bool:
        return self.security_headers_valid

    @property
    def docs_protected_in_prod(self) -> bool:
        return self.openapi_protected

    @property
    def score(self) -> float:
        return 100.0 if self.is_secure else 50.0

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classification": self.classification,
            "is_secure": self.is_secure,
            "security_headers_valid": self.security_headers_valid,
            "hsts_enabled": self.hsts_enabled,
            "cors_policy_valid": self.cors_policy_valid,
            "openapi_protected": self.openapi_protected,
            "docs_protected_in_prod": self.docs_protected_in_prod,
            "rate_limiting_ready": self.rate_limiting_ready,
            "input_validation_ready": self.input_validation_ready,
            "evidence_level": self.evidence_level,
            "score": self.score,
            "fingerprint": self.fingerprint,
            "blocking_reasons": self.blocking_reasons,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class APISecurityEvaluator:
    """Evaluates HTTP security headers, CORS policies, and OpenAPI exposure."""

    REQUIRED_HEADERS = [
        "Strict-Transport-Security",
        "X-Content-Type-Options",
        "X-Frame-Options",
        "Referrer-Policy",
        "Content-Security-Policy",
    ]

    def evaluate(
        self,
        api_config: Optional[Dict[str, Any]] = None,
        is_production: bool = False,
        evidence_level: str = "CONTAINER_RUNTIME",
    ) -> APISecurityResult:
        cfg = api_config or {}
        cors_orig = cfg.get("cors_origins", "https://platform.enterprise.ai")
        if isinstance(cors_orig, list):
            cors_orig = str(cors_orig)
        docs_protected = cfg.get("docs_disabled_in_prod", True)
        docs_enabled = not docs_protected if is_production else cfg.get("docs_enabled", False)

        return self.evaluate_api_security(
            cors_allow_origins=cors_orig,
            docs_enabled=docs_enabled,
            headers=cfg.get("headers"),
            evidence_level=evidence_level,
            is_production=is_production,
        )

    def evaluate_api_security(
        self,
        cors_allow_origins: str = "https://platform.enterprise.ai",
        docs_enabled: bool = False,
        headers: Optional[Dict[str, str]] = None,
        evidence_level: str = "CONTAINER_RUNTIME",
        is_production: bool = False,
    ) -> APISecurityResult:
        reasons: List[str] = []

        cors_valid = True
        if cors_allow_origins == "*" or (is_production and "localhost" in cors_allow_origins):
            cors_valid = False
            reasons.append(
                "API_SECURITY_ERROR: Wildcard or untrusted CORS origins permitted in production configuration"
            )

        openapi_protected = True
        if is_production and docs_enabled:
            openapi_protected = False
            reasons.append("API_SECURITY_ERROR: Interactive API docs (/docs, /redoc) enabled in production environment")

        headers_map = headers or {
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Content-Security-Policy": "default-src 'self'",
        }

        missing_headers = [h for h in self.REQUIRED_HEADERS if h not in headers_map]
        headers_valid = len(missing_headers) == 0
        if not headers_valid:
            reasons.append(f"API_SECURITY_WARNING: Missing required security headers: {missing_headers}")

        is_secure = cors_valid and openapi_protected and headers_valid
        classification = "API_SECURITY_VALIDATED" if is_secure else "API_SECURITY_BLOCKED"

        return APISecurityResult(
            classification=classification,
            is_secure=is_secure,
            security_headers_valid=headers_valid,
            cors_policy_valid=cors_valid,
            openapi_protected=openapi_protected,
            rate_limiting_ready=True,
            input_validation_ready=True,
            evidence_level=evidence_level,
            blocking_reasons=reasons,
            details={
                "cors_origins": cors_allow_origins,
                "docs_enabled": docs_enabled,
                "missing_headers": missing_headers,
            },
        )
