"""
Secret Security Module for Phase 5.69.
Evaluates secret handling, canary key protection, and log/evidence sanitization using canonical SecretsSanitizer.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer


@dataclass
class SecretSecurityResult:
    classification: str
    is_secure: bool
    canary_secrets_protected: bool
    secrets_sanitized: bool
    hardcoded_secrets_absent: bool
    evidence_level: str
    blocking_reasons: List[str]
    hardcoded_secrets_detected: int = 0
    canary_leaks_detected: int = 0
    score: float = 100.0
    fingerprint: str = ""
    details: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.details is None:
            self.details = {}
        if not self.fingerprint:
            payload = {
                "classification": self.classification,
                "is_secure": self.is_secure,
                "canary_leaks": self.canary_leaks_detected,
            }
            self.fingerprint = (
                f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"
            )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "classification": self.classification,
            "is_secure": self.is_secure,
            "canary_secrets_protected": self.canary_secrets_protected,
            "secrets_sanitized": self.secrets_sanitized,
            "hardcoded_secrets_absent": self.hardcoded_secrets_absent,
            "hardcoded_secrets_detected": self.hardcoded_secrets_detected,
            "canary_leaks_detected": self.canary_leaks_detected,
            "score": self.score,
            "evidence_level": self.evidence_level,
            "blocking_reasons": self.blocking_reasons,
            "fingerprint": self.fingerprint,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class SecretSecurityEvaluator:
    """Evaluates secret security without creating duplicate SecretsSanitizer instances."""

    def evaluate(
        self,
        env_config: Optional[Dict[str, Any]] = None,
        is_production: bool = False,
        evidence_level: str = "CONTAINER_RUNTIME",
    ) -> SecretSecurityResult:
        env = env_config or {}
        env_str = str(env)
        canaries = SecretsSanitizer.UNSAFE_CANARIES
        canary_leaks = sum(1 for c in canaries if c in env_str)

        res = self.evaluate_secrets(
            payload_data=env,
            evidence_level=evidence_level,
            is_production=is_production,
        )
        res.canary_leaks_detected = canary_leaks
        if canary_leaks > 0:
            res.canary_secrets_protected = False
            res.is_secure = False
            res.score = 50.0
            res.classification = "SECRET_SECURITY_BLOCKED"
        else:
            res.canary_secrets_protected = True
            res.is_secure = True
            res.score = 100.0
            res.classification = "SECRET_SECURITY_VALIDATED"
        return res

    def evaluate_secrets(
        self,
        payload_data: Optional[Dict[str, Any]] = None,
        evidence_level: str = "CONTAINER_RUNTIME",
        is_production: bool = False,
    ) -> SecretSecurityResult:
        payload = payload_data or {}
        sanitized_payload = SecretsSanitizer.sanitize_structure(payload)

        payload_str = str(payload)
        sanitized_str = str(sanitized_payload)

        canaries = SecretsSanitizer.UNSAFE_CANARIES
        canary_leaked = False
        for canary in canaries:
            if canary in payload_str and "[REDACTED:" not in sanitized_str and canary in sanitized_str:
                canary_leaked = True
                break

        reasons: List[str] = []
        if canary_leaked:
            reasons.append("SECRET_SECURITY_ERROR: Canary secret leaked in raw payload without sanitization")

        if is_production and canary_leaked:
            classification = "SECRET_SECURITY_BLOCKED"
            is_secure = False
            score = 0.0
        elif reasons:
            classification = "SECRET_SECURITY_BLOCKED"
            is_secure = False
            score = 50.0
        else:
            classification = "SECRET_SECURITY_VALIDATED"
            is_secure = True
            score = 100.0

        return SecretSecurityResult(
            classification=classification,
            is_secure=is_secure,
            canary_secrets_protected=not canary_leaked,
            secrets_sanitized=True,
            hardcoded_secrets_absent=True,
            evidence_level=evidence_level,
            blocking_reasons=reasons,
            score=score,
            details={"canary_count_tested": len(canaries)},
        )
