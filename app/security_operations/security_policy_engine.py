"""
Security Policy Engine Module for Phase 5.69.
Enforces deterministic security rules and actions (ALLOW, WARN, BLOCK, MANUAL_REVIEW_REQUIRED).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional

from app.deployment.secrets import SecretsSanitizer


class SecurityPolicyAction(str, Enum):
    ALLOW = "ALLOW"
    WARN = "WARN"
    BLOCK = "BLOCK"
    MANUAL_REVIEW_REQUIRED = "MANUAL_REVIEW_REQUIRED"


@dataclass
class SecurityPolicyRule:
    rule_id: str
    name: str
    category: str
    action_if_triggered: SecurityPolicyAction
    description: str = ""


@dataclass
class SecurityPolicy:
    policy_id: str
    name: str
    rules: List[SecurityPolicyRule]



@dataclass
class SecurityPolicyResult:
    overall_action: SecurityPolicyAction
    is_blocking: bool
    triggered_rules: List[Dict[str, Any]]
    evidence_level: str
    is_production: bool = False
    fingerprint: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        if not self.fingerprint:
            payload = {
                "action": self.action,
                "blocking": self.is_blocking,
                "triggered": len(self.triggered_rules),
            }
            self.fingerprint = f"sha256:{hashlib.sha256(json.dumps(payload, sort_keys=True).encode('utf-8')).hexdigest()}"

    @property
    def action(self) -> str:
        return self.overall_action.value if isinstance(self.overall_action, Enum) else str(self.overall_action)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall_action": self.action,
            "action": self.action,
            "is_blocking": self.is_blocking,
            "triggered_rules": SecretsSanitizer.sanitize_structure(self.triggered_rules),
            "evidence_level": self.evidence_level,
            "is_production": self.is_production,
            "fingerprint": self.fingerprint,
            "details": SecretsSanitizer.sanitize_structure(self.details),
        }


class SecurityPolicyEngine:
    """Evaluates platform observations against configured security policy rules."""

    def __init__(
        self,
        min_production_score: float = 90.0,
        custom_rules: Optional[List[SecurityPolicyRule]] = None,
    ) -> None:
        self.min_production_score = min_production_score
        self.rules = custom_rules or [
            SecurityPolicyRule("R001", "Secret Exposure Policy", "SECRET_EXPOSURE", SecurityPolicyAction.BLOCK, "Block if raw secrets detected"),
            SecurityPolicyRule("R002", "Insecure Configuration Policy", "INSECURE_CONFIGURATION", SecurityPolicyAction.BLOCK, "Block on insecure configuration"),
            SecurityPolicyRule("R003", "Weak Authentication Policy", "WEAK_AUTHENTICATION", SecurityPolicyAction.BLOCK, "Block on weak auth"),
            SecurityPolicyRule("R004", "Unsafe CORS Policy", "UNSAFE_CORS", SecurityPolicyAction.BLOCK, "Block wildcard CORS in production/staging"),
            SecurityPolicyRule("R005", "Missing Security Headers Policy", "MISSING_SECURITY_HEADERS", SecurityPolicyAction.WARN, "Warn on missing headers"),
            SecurityPolicyRule("R006", "Invalid Artifact Policy", "INVALID_ARTIFACT", SecurityPolicyAction.BLOCK, "Block on digest mismatch"),
            SecurityPolicyRule("R007", "Untrusted Dependency Policy", "UNTRUSTED_DEPENDENCY", SecurityPolicyAction.MANUAL_REVIEW_REQUIRED, "Manual review for unpinned deps"),
            SecurityPolicyRule("R008", "Vulnerable Container Policy", "VULNERABLE_CONTAINER", SecurityPolicyAction.BLOCK, "Block container running as root"),
            SecurityPolicyRule("R009", "Unauthorized Access Policy", "UNAUTHORIZED_ACCESS", SecurityPolicyAction.BLOCK, "Block on RBAC violation"),
            SecurityPolicyRule("R010", "Audit Failure Policy", "AUDIT_FAILURE", SecurityPolicyAction.BLOCK, "Block on audit tamper failure"),
        ]

    def evaluate_policy(
        self,
        posture_result: Any,
        is_production: bool = False,
        evidence_level: str = "CONTAINER_RUNTIME",
    ) -> SecurityPolicyResult:
        findings = []
        if hasattr(posture_result, "critical_findings"):
            for f in posture_result.critical_findings:
                findings.append({"category": "SECRET_EXPOSURE", "finding": f})
        
        res = self.evaluate_policies(findings, evidence_level)
        res.is_production = is_production
        
        # Check production threshold
        score = posture_result.score if hasattr(posture_result, 'score') else 100.0
        if is_production and score < self.min_production_score:
            res.overall_action = SecurityPolicyAction.BLOCK
            res.is_blocking = True

        return res

    def evaluate_policies(
        self,
        security_findings: List[Dict[str, Any]],
        evidence_level: str = "CONTAINER_RUNTIME",
    ) -> SecurityPolicyResult:
        triggered = []
        overall = SecurityPolicyAction.ALLOW
        is_blocking = False

        category_findings = {f.get("category"): f for f in security_findings if "category" in f}

        for rule in self.rules:
            if rule.category in category_findings:
                finding = category_findings[rule.category]
                triggered.append({
                    "rule_id": rule.rule_id,
                    "name": rule.name,
                    "category": rule.category,
                    "action": rule.action_if_triggered.value,
                    "finding": finding,
                })
                if rule.action_if_triggered == SecurityPolicyAction.BLOCK:
                    overall = SecurityPolicyAction.BLOCK
                    is_blocking = True
                elif rule.action_if_triggered == SecurityPolicyAction.MANUAL_REVIEW_REQUIRED and overall != SecurityPolicyAction.BLOCK:
                    overall = SecurityPolicyAction.MANUAL_REVIEW_REQUIRED
                elif rule.action_if_triggered == SecurityPolicyAction.WARN and overall not in (SecurityPolicyAction.BLOCK, SecurityPolicyAction.MANUAL_REVIEW_REQUIRED):
                    overall = SecurityPolicyAction.WARN

        return SecurityPolicyResult(
            overall_action=overall,
            is_blocking=is_blocking,
            triggered_rules=triggered,
            evidence_level=evidence_level,
            details={"triggered_count": len(triggered)},
        )
