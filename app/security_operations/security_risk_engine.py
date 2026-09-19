"""
Security Risk Engine Module for Phase 5.69.
Calculates security risk score (likelihood x impact) and policy actions.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer


class RiskLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RiskPolicyAction(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"
    BLOCK = "BLOCK"


@dataclass
class SecurityRisk:
    risk_id: str
    category: str
    likelihood: float  # 0.0 to 1.0
    impact: float  # 0.0 to 1.0
    risk_score: float  # likelihood x impact (0.0 to 1.0)
    level: RiskLevel
    policy_action: RiskPolicyAction
    details: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "risk_id": self.risk_id,
            "category": self.category,
            "likelihood": self.likelihood,
            "impact": self.impact,
            "risk_score": self.risk_score,
            "level": self.level.value if isinstance(self.level, Enum) else str(self.level),
            "policy_action": (
                self.policy_action.value if isinstance(self.policy_action, Enum) else str(self.policy_action)
            ),
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


@dataclass
class RiskAssessment:
    overall_risk_level: RiskLevel
    overall_policy_action: RiskPolicyAction
    max_risk_score: float
    is_blocking: bool
    risks: List[SecurityRisk]
    evidence_level: str
    fingerprint: str = ""

    def __post_init__(self):
        if not self.fingerprint:
            payload = {
                "level": (
                    self.overall_risk_level.value
                    if isinstance(self.overall_risk_level, Enum)
                    else str(self.overall_risk_level)
                ),
                "max_score": self.max_risk_score,
                "blocking": self.is_blocking,
            }
            self.fingerprint = (
                f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"
            )

    @property
    def overall_risk_score(self) -> float:
        return self.max_risk_score

    def to_dict(self) -> Dict[str, Any]:
        lvl_str = (
            self.overall_risk_level.value if isinstance(self.overall_risk_level, Enum) else str(self.overall_risk_level)
        )
        act_str = (
            self.overall_policy_action.value
            if isinstance(self.overall_policy_action, Enum)
            else str(self.overall_policy_action)
        )
        return {
            "overall_risk_level": lvl_str,
            "overall_policy_action": act_str,
            "max_risk_score": self.max_risk_score,
            "overall_risk_score": self.overall_risk_score,
            "is_blocking": self.is_blocking,
            "risks": [r.to_dict() for r in self.risks],
            "evidence_level": self.evidence_level,
            "fingerprint": self.fingerprint,
        }


class SecurityRiskEngine:
    """Calculates risk score = likelihood x impact and enforces risk policy rules."""

    def assess_risk(
        self,
        posture_score: float = 100.0,
        vulnerabilities: Optional[List[Any]] = None,
        active_exceptions: Optional[List[Any]] = None,
        is_production: bool = False,
        evidence_level: str = "CONTAINER_RUNTIME",
    ) -> RiskAssessment:
        vuln_list = vulnerabilities or []
        crit_count = sum(1 for v in vuln_list if getattr(v, "severity", "") in ("CRITICAL", RiskLevel.CRITICAL))
        high_count = sum(1 for v in vuln_list if getattr(v, "severity", "") in ("HIGH", RiskLevel.HIGH))

        res = self.evaluate_risk(
            critical_vuln_count=crit_count,
            high_vuln_count=high_count,
            secret_leak_detected=(posture_score < 50.0),
            audit_tampered=False,
            evidence_level=evidence_level,
        )

        if is_production and posture_score < 90.0:
            res.is_blocking = True
            res.overall_risk_level = RiskLevel.HIGH
            res.overall_policy_action = RiskPolicyAction.BLOCK

        return res

    def evaluate_risk(
        self,
        critical_vuln_count: int = 0,
        high_vuln_count: int = 0,
        secret_leak_detected: bool = False,
        audit_tampered: bool = False,
        evidence_level: str = "CONTAINER_RUNTIME",
    ) -> RiskAssessment:
        risks: List[SecurityRisk] = []

        if secret_leak_detected:
            score = 1.0 * 1.0
            risks.append(
                SecurityRisk(
                    "R-SEC-01",
                    "SECRET_EXPOSURE",
                    1.0,
                    1.0,
                    score,
                    RiskLevel.CRITICAL,
                    RiskPolicyAction.BLOCK,
                    {"leak": True},
                )
            )

        if audit_tampered:
            score = 1.0 * 0.95
            risks.append(
                SecurityRisk(
                    "R-AUD-01",
                    "AUDIT_TAMPERING",
                    1.0,
                    0.95,
                    score,
                    RiskLevel.CRITICAL,
                    RiskPolicyAction.BLOCK,
                    {"tampered": True},
                )
            )

        if critical_vuln_count > 0:
            score = 0.9 * 0.9
            risks.append(
                SecurityRisk(
                    "R-VULN-01",
                    "CRITICAL_VULNERABILITY",
                    0.9,
                    0.9,
                    score,
                    RiskLevel.CRITICAL,
                    RiskPolicyAction.BLOCK,
                    {"count": critical_vuln_count},
                )
            )

        if high_vuln_count > 0:
            score = 0.7 * 0.8
            risks.append(
                SecurityRisk(
                    "R-VULN-02",
                    "HIGH_VULNERABILITY",
                    0.7,
                    0.8,
                    score,
                    RiskLevel.HIGH,
                    RiskPolicyAction.MANUAL_REVIEW_REQUIRED,
                    {"count": high_vuln_count},
                )
            )

        if not risks:
            risks.append(
                SecurityRisk(
                    "R-BASELINE",
                    "BASELINE_RISK",
                    0.1,
                    0.1,
                    0.01,
                    RiskLevel.LOW,
                    RiskPolicyAction.ALLOW,
                    {"status": "HEALTHY"},
                )
            )

        max_score = max(r.risk_score for r in risks)
        has_critical = any(r.level == RiskLevel.CRITICAL for r in risks)
        has_high = any(r.level == RiskLevel.HIGH for r in risks)

        if has_critical:
            overall_level = RiskLevel.CRITICAL
            overall_action = RiskPolicyAction.BLOCK
            is_blocking = True
        elif has_high:
            overall_level = RiskLevel.HIGH
            overall_action = RiskPolicyAction.MANUAL_REVIEW_REQUIRED
            is_blocking = False
        else:
            overall_level = RiskLevel.LOW
            overall_action = RiskPolicyAction.ALLOW
            is_blocking = False

        return RiskAssessment(
            overall_risk_level=overall_level,
            overall_policy_action=overall_action,
            max_risk_score=max_score,
            is_blocking=is_blocking,
            risks=risks,
            evidence_level=evidence_level,
        )
